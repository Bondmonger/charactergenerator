import random
import attributes
import hitpoints
import agevalues
import heightweight
import charalign
import generatecharacter
import selectclass
import datalocus
from enum import Enum
import json
import os
# import time


class CharacterEventType(Enum):                         # events emitted by Character operations
    CHARACTER_RENAMED, XP_AWARDED, LEVEL_CHANGED = "character_renamed", "xp_awarded", "level_changed"
    ATTRIBUTE_CHANGED, AGE_CHANGED, CHARACTER_TRANSFORMED = "attribute_changed", "age_changed", "character_transformed"


def roll(b):  # rolls a single die of "b" sides
    return random.randrange(1, b + 1)


class Character:
    def __init__(self, level=1, race='', gender='random', classes=(), attrib_list=(), event_bus=None,
                 auto_dual_class=False):
        # start = time.time()
        self.event_bus = event_bus                      # optional EventBus for domain event emission
        self.dual_class = None                          # populated at transition; see brief for schema
        self.intended_class = None                      # 'Bard' for bard-track chars only; else None
        self.character_name = ''
        # print("classes: ", classes)
        _designated_bard = (list(classes) == ['Bard'])     # captured before anything mutates classes
        if _designated_bard:
            # Bard is not in the race/class CSV — must be Human or Half-elf.
            # Use the Fighter weighted race distribution, filtered to eligible races,
            # so the Human/Half-elf ratio reflects the same proportions as bulk_maker.
            if len(race) > 0:
                self.race = race
            else:
                bard_race_weights = selectclass.weighted_race('Fighter')
                eligible = {r: w for r, w in bard_race_weights.items()
                            if r in ('Human', 'Half-elf')}
                self.race = random.choices(list(eligible.keys()),
                                           weights=list(eligible.values()), k=1)[0]
            self.classes = ['Fighter']
        else:
            self.race = selectclass.race_from_class(classes) if len(race) == 0 else race            # 'Gray Elf'
            self.classes = selectclass.random_class(self.race) if len(classes) == 0 else list(classes)  # ['Fighter', 'Thief']
        intended_classes = self.classes[:]          # snapshot before methodvi can mutate self.classes via _demotion
        self.alignment = self.calculate_alignment()
        # Designated bards: roll attributes against Bard minimums (Str15 Int12 Wis15 Dex15 Con10 Cha15).
        # self.classes is already ['Fighter'] but methodvi must see ['Bard'] to target the right minimums.
        methodvi_classes = ['Bard'] if _designated_bard else self.classes
        self.attributes = attributes.methodvi(self.race, methodvi_classes) if len(attrib_list) == 0 else attrib_list
        self.excess, self.attributes = self.attributes.pop(1), self.attributes[0]   # excess = same format as attributes
        self.gender = heightweight.random_gender() if gender == "random" else gender            # female
        if self.classes[0] == '0-level':    # these units throw an error when AC/THAC0/movement are calculated
            self.age = agevalues.generate_age(self.race, intended_classes, level)
            for k in self.attributes:       # set all attributes to 10 pending monsters.json integration
                self.attributes[k] = 10
            self.attributes['Exc'] = 0
            self.display_class, self.xp, self.level, self.hp = '0-level', 0, [0], 5
            self.size = heightweight.size(self.race, self.gender)
            return
        self.age = agevalues.generate_age(self.race, self.classes, level)
        pre_age_attrs = dict(self.attributes)               # snapshot for probabilistic bard eligibility check
        for k, v in self.attributes.items():
            self.attributes[k] = self.attributes[k] + self.age[3][k]
        # ------------------------------------------------------------------
        # Bard interception — must run after attributes are rolled.
        # Designated path: always set the flag; eligibility is re-checked at
        # the transition point (level 5–7) by which time age penalties will
        # have resolved.
        # Probabilistic path: checked against pre-age attributes so that age
        # penalties don't silently disqualify a qualifying roll.
        # ------------------------------------------------------------------
        if _designated_bard:
            self.intended_class = 'Bard'                    # unconditional — check deferred to transition point
        elif (self.classes == ['Fighter']
              and self.race in ('Human', 'Half-elf')
              and selectclass.bard_eligible(pre_age_attrs)):
            # Plain Fighter who qualifies: bard track competes equally with
            # all other dual-class destinations available to this character.
            bard_options = selectclass.dual_class_options(
                'Fighter', self.attributes, self.alignment, self.race,
                bard_track=True)
            if bard_options and random.random() < 1 / len(bard_options):
                self.intended_class = 'Bard'
        self.display_class = generatecharacter.display_classes(self.classes)
        self.xp = generatecharacter.pc_xp(level)                                    # generates xp from mean
        self.level = generatecharacter.generate_level(self.attributes, self.classes, self.race, self.xp, self.excess)
        self.level, next_level_raw = self.level['level'], self.level.pop('next_level')
        self.next_level = [int(next_level_raw[0]), next_level_raw[1]]
        self.display_level = generatecharacter.display_level(self.level)
        self.hp_history = hitpoints.generate_hp(self.classes, self.level, self.attributes['Con'])
        self.modify_age(0)  # this is to factor in modifiers from the age increments in generate_level()
        self.size = heightweight.size(self.race, self.gender)
        self.hp = generatecharacter.flatten(self.hp_history)
        if auto_dual_class:
            self._apply_auto_dual_class(max(self.level), self.xp)
        return

    def change_attribute(self, attr: str, adjustment: int) -> None:  # public domain wrapper for modify_attribute
        old_value = self.attributes[attr]
        self.modify_attribute(attr, adjustment)
        if self.event_bus:
            self.event_bus.emit(CharacterEventType.ATTRIBUTE_CHANGED, {
                'character': self, 'name': self.character_name,
                'attr': attr, 'old_value': old_value, 'new_value': self.attributes[attr]})

    def rename(self, new_name: str) -> None:            # renames character and emits CHARACTER_RENAMED event
        old_name = self.character_name
        self.character_name = new_name
        if self.event_bus:
            self.event_bus.emit(CharacterEventType.CHARACTER_RENAMED, {
                'character': self, 'old_name': old_name, 'new_name': new_name})

    def award_xp(self, amount: int) -> str:             # awards xp, recalculates level, emits events
        self.modify_xp(amount)
        message = self.calculate_level(0)
        # Freeze original class at its transition level — it never gains XP after dual-class
        if self.dual_class is not None:
            orig = self.dual_class['original']
            orig_level = self.dual_class['original_level']
            if orig in self.classes:                    # post-crossover: clamp original back if clobbed
                idx = self.classes.index(orig)
                self.level[idx] = orig_level
        if self.event_bus:
            self.event_bus.emit(CharacterEventType.XP_AWARDED, {
                'character': self, 'name': self.character_name, 'amount': amount, 'total_xp': self.xp})
            if message:
                self.event_bus.emit(CharacterEventType.LEVEL_CHANGED, {
                    'character': self, 'name': self.character_name, 'message': message, 'level': self.level})
        return message

    def _flatten(self) -> int:      # wrapper preventing multiclass HP halving (for dual-class characters)
        divisor = 1 if self.dual_class is not None else None
        return generatecharacter.flatten(self.hp_history, divisor)

    def drain_level(self) -> str:                       # drains one level and emits LEVEL_CHANGED event
        message = self.calculate_level(-1)
        if self.event_bus and message:
            self.event_bus.emit(CharacterEventType.LEVEL_CHANGED, {
                'character': self, 'name': self.character_name, 'message': message, 'level': self.level})
        return message

    def display_strength(self):                                     # calculates a displayable strength
        archetypes = []
        for character_class in self.classes:
            archetypes.append(datalocus.archetype(character_class))
        if self.attributes['Str'] == 18 and self.attributes['Exc'] > 0 and "Fighter" in archetypes:
            displaystr = str(self.attributes['Str']) + '/' + str(self.attributes['Exc'])[-2:].zfill(2)
        else:
            displaystr = str(self.attributes['Str'])
        return displaystr

    def modify_str(self, adjustment):
        max_strength = datalocus.racial_maximums(self.race)[0]     # used at the end
        self.attributes['Str'] += adjustment
        if self.attributes['Str'] > 17:
            max_racial_str = datalocus.exceptional_str(self.race)
            while self.attributes['Str'] > 18:                      # converts strength above 18 into excess points
                self.attributes['Str'] -= 1
                self.excess['Str'] += 1
            self.attributes['Exc'] += self.excess['Str'] * 10       # dumps excess points into exc. strength (*10)
            self.excess['Str'] = 0                                  # tares excess to zero
            if self.attributes['Exc'] > max_racial_str:
                while self.attributes['Exc'] > max_racial_str + 9:
                    self.excess['Str'] += 1
                    self.attributes['Exc'] -= 10
                self.attributes['Exc'] = max_racial_str             # reduces exc. strength to racial max (if necessary)
            if self.attributes['Exc'] > 100:
                while self.attributes['Exc'] > 100:
                    self.attributes['Str'] += 1
                    self.attributes['Exc'] -= 10
                self.attributes['Exc'] = 100                        # converts +00 percentile scores into 19+ strength
        if self.attributes['Str'] > max_strength:                   # for low max strength races (halfling, drow, etc)
            self.excess['Str'] += self.attributes['Str'] - max_strength
            self.attributes['Str'] = max_strength
        return

    def modify_con(self, adjustment):
        max_constitution = datalocus.racial_maximums(self.race)[4]
        self.attributes['Con'] += self.excess['Con'] + adjustment
        self.excess['Con'] = 0                                                          # tares excess to zero
        if self.attributes['Con'] > max_constitution:
            self.excess['Con'] += self.attributes['Con'] - max_constitution
            self.attributes['Con'] = max_constitution
        if self.dual_class is not None and 'fighter_level' in self.dual_class:
            self._recompute_bard_con()                          # Bard stage 3: three-slot con
        elif self.dual_class is not None:
            self._recompute_dual_class_con()
        else:
            hpcalcs = [datalocus.call_hp(c) for c in self.classes]
            roll_lists_copy = [list(h) for h in self.hp_history[:-1]]
            hitpoints.con_bonus(roll_lists_copy, hpcalcs, self.attributes['Con'])
            self.hp_history[-1] = roll_lists_copy[-1]
        self.hp = self._flatten()
        return

    def _recompute_dual_class_con(self):                    # recomputs trailing con bonus list for dual-class chars
        con = self.attributes['Con']
        bonus = datalocus.con_hpbonus(con)
        
        def _class_con(ch_class, absolute_level):
            hpcalcs = datalocus.call_hp(ch_class)           # hpcalcs[1] is 1st level hid dice (Ranger, Monk)
            cap = hpcalcs[6]                                # max con bonus for this class
            temp = cap if bonus > cap else bonus
            temp *= hpcalcs[7]                              # barbarian x2 rate (1 for all others)
            raw_mult = hpcalcs[1] + absolute_level - 1      # effective dice count at this level
            multiplier = min(raw_mult, hpcalcs[4])          # cap at name level threshold
            return temp * multiplier
        dest_class, dest_level = self.classes[0], self.level[0]
        orig_class, orig_level = self.dual_class['original'], self.dual_class['original_level']
        dest_con = max(0, _class_con(dest_class, dest_level) - _class_con(dest_class, orig_level))
        orig_con = _class_con(orig_class, orig_level)
        self.hp_history[-1] = [dest_con, orig_con]

    def _recompute_bard_con(self):                              # recomputes three-slot con list for Bard stage 3
        """Bard con rules:
        - Bard slot: 0 until Bard level exceeds original_level (frozen Thief level); then accrues normally.
        - Thief slot: frozen at transition — read from original_hp[-1][0], never recomputed.
        - Fighter slot: frozen at transition — read from original_hp[-1][1], never recomputed.
        Con changes (modify_con) only affect the Bard slot; the frozen slots are immutable.
        """
        con = self.attributes['Con']
        bonus = datalocus.con_hpbonus(con)

        def _class_con(ch_class, absolute_level):
            hpcalcs = datalocus.call_hp(ch_class)
            cap = hpcalcs[6]
            temp = cap if bonus > cap else bonus
            temp *= hpcalcs[7]
            raw_mult = hpcalcs[1] + absolute_level - 1
            multiplier = min(raw_mult, hpcalcs[4])
            return temp * multiplier

        bard_level  = self.level[0]
        thief_level = self.dual_class['original_level']         # frozen Thief level

        # Bard con: 0 until bard_level > thief_level, then accrues for levels above thief_level
        if bard_level > thief_level:
            bard_con = max(0, _class_con('Bard', bard_level) - _class_con('Bard', thief_level))
        else:
            bard_con = 0

        # Thief and Fighter con are frozen at the moment of the Thief->Bard transition.
        # original_hp[-1] = [thief_con, fighter_con] as captured in initiate_dual_class().
        frozen_con  = self.dual_class['original_hp'][-1]
        thief_con   = frozen_con[0]
        fighter_con = frozen_con[1]
        self.hp_history[-1] = [bard_con, thief_con, fighter_con]

    def modify_wis(self, adjustment):
        max_wisdom = 25                                                                 # removes Wis max in all cases
        self.attributes['Wis'] += self.excess['Wis'] + adjustment
        self.excess['Wis'] = 0                                                          # tares excess to zero
        if self.attributes['Wis'] > max_wisdom:
            self.excess['Wis'] += self.attributes['Wis'] - max_wisdom
            self.attributes['Wis'] = max_wisdom
        return

    def modify_cha(self, adjustment):
        starting_modifier = datalocus.comeliness_bonus(self.attributes['Cha'])
        max_charisma = datalocus.racial_maximums(self.race)[5]
        self.attributes['Cha'] += self.excess['Cha'] + adjustment
        self.excess['Cha'] = 0                                                          # tares excess to zero
        if self.attributes['Cha'] > max_charisma:
            self.excess['Cha'] += self.attributes['Cha'] - max_charisma
            self.attributes['Cha'] = max_charisma
        end_modifier = datalocus.comeliness_bonus(self.attributes['Cha'])
        self.attributes['Com'] += end_modifier - starting_modifier
        return

    def modify_other_att(self, adjustment, attribute):
        ord_attrs = ['Str', 'Int', 'Wis', 'Dex', 'Con', 'Cha', 'Com']
        max_att = datalocus.racial_maximums(self.race)[ord_attrs.index(attribute)]      # racial max by attr index pos.
        self.attributes[attribute] += self.excess[attribute] + adjustment
        self.excess[attribute] = 0                                                      # tares excess to zero
        if self.attributes[attribute] > max_att:
            self.excess[attribute] += self.attributes[attribute] - max_att
            self.attributes[attribute] = max_att
        return

    def modify_attribute(self, attr, adjustment):
        if self.excess[attr] > 0 > adjustment:
            while adjustment < 0:
                self.excess[attr] -= 1
                adjustment += 1
            if adjustment == 0:
                return
        if attr == 'Str':                           # because of exceptional strength
            self.modify_str(adjustment)
        if attr == 'Con':                           # because it may trigger an hp adjustment
            self.modify_con(adjustment)
        if attr == 'Wis':                           # because it is uncapped (unlike other attributes)
            self.modify_wis(adjustment)
        if attr == 'Cha':                           # because it may trigger a comeliness adjustment
            self.modify_cha(adjustment)
        if attr in ['Int', 'Dex', 'Com']:           # no special considerations
            self.modify_other_att(adjustment, attr)
        self.calculate_level()
        next_level_raw = generatecharacter.generate_level(self.attributes, self.classes, self.race, self.xp,
                                                           self.excess).pop('next_level')
        self.next_level = [int(next_level_raw[0]), next_level_raw[1]]
        return

    def modify_age(self, adjustment):
        starting_category, starting_atts, atts_mod = self.age[1], [], []
        ord_attrs = ['Str', 'Int', 'Wis', 'Dex', 'Con', 'Cha', 'Com']
        self.age[0] += adjustment                                   # updates age number
        self.age[1] = datalocus.age_cat(self.race, self.age[0])[0]  # updates age category
        if starting_category != self.age[1]:
            for attrs in range(7):
                starting_atts.append(datalocus.age_adj(starting_category)[attrs])
                atts_mod.append(datalocus.age_adj(self.age[1])[attrs] - starting_atts[attrs])
            attrs_mod_dict = dict(zip(ord_attrs, atts_mod))
            for k, v in attrs_mod_dict.items():
                self.modify_attribute(k, v)
            if self.age[0] > self.age[4]:
                self.age[1] = "dead"
            if self.event_bus:
                self.event_bus.emit(CharacterEventType.AGE_CHANGED, {
                    'character': self, 'name': self.character_name,
                    'old_category': starting_category, 'new_category': self.age[1],
                    'age': self.age[0]})
        return

    def modify_xp(self, adjustment):
        if self.xp + adjustment >= int(generatecharacter.impending_mean_xp(self.xp)):
            self.modify_age(1)
        self.xp += adjustment
        return

    def wightify(self):                         # important - self.movement is the check used to flag non-classed units
        from mobstatblock import MobStatblock   # note that preserved_height converts feet (in monsters.json) to inches
        preserved_height, preserved_weight, preserved_int, preserved_wis = \
            self.size[0], self.size[1], self.attributes['Int'], self.attributes['Wis']
        monsters_path = os.path.join(os.path.dirname(__file__), 'monsters.json')
        with open(monsters_path, encoding='utf-8') as f:
            mob_data = json.load(f)
        entry = mob_data['Wight']['Wight']
        MobStatblock.apply_to(self, entry)
        self.size[0], self.size[1], self.attributes['Int'], self.attributes['Wis'] = \
            preserved_height, preserved_weight, preserved_int, preserved_wis
        message = "This character has become a WIGHT!"
        if self.event_bus:
            self.event_bus.emit(CharacterEventType.CHARACTER_TRANSFORMED,
                                {'character': self, 'name': self.character_name,
                                 'message': message, 'transformation': 'wight'})
        return message

    # ------------------------------------------------------------------
    # Dual-class helpers
    # ------------------------------------------------------------------

    def _apply_auto_dual_class(self, final_level: int, total_xp: int) -> None:     # probability for generated NPCs to be dual-class
        if len(self.classes) != 1:                                  # only fires for single-class units
            return
        import selectclass as sc
        original_class = self.classes[0]
        is_bard_track = (self.intended_class == 'Bard')

        # ---- Determine valid transition window and per-level probability -------
        # Bard-track windows are strict: Fighter 5–7, Thief 5–8.
        # Bard-track probabilities are hardcoded: 60% per Fighter level (93.6%
        # combined), 50% per Thief level (93.8% combined), giving ~87.8% overall.
        # Standard dual-class: any level >= 2, probability from dualprobs CSV.
        if is_bard_track and original_class == 'Fighter':
            window = range(5, 8)        # levels 5, 6, 7
            per_level_prob = 0.60
        elif is_bard_track and original_class == 'Thief':
            window = range(5, 9)        # levels 5, 6, 7, 8
            per_level_prob = 0.50
        else:
            window = range(2, final_level + 1)
            per_level_prob = None       # use dual_class_transition_prob() from CSV

        transition_level = None
        for lvl in range(1, final_level + 1):
            if lvl not in window:
                continue
            if per_level_prob is not None:
                # Bard track: last level in window is always a guaranteed transition if eligible
                prob = 1.0 if lvl == window[-1] else per_level_prob
            else:
                prob = sc.dual_class_transition_prob(original_class, lvl)
            if prob > 0 and random.random() < prob:
                transition_level = lvl
                break

        if transition_level is None:
            return

        # ---- For bard track: destination is always Thief (stage 1→2) ---------
        if is_bard_track:
            options = ['Thief'] if sc.bard_eligible(self.attributes) else []
        else:
            options = sc.dual_class_options(
                original_class, self.attributes, self.alignment, self.race)
        if not options:
            return
        destination = random.choice(options)
        self.level = [transition_level]                             # captures unit state ahead of HP history freeze
        self.hp_history = hitpoints.generate_hp([original_class], [transition_level], self.attributes['Con'])
        attrs_list = list(self.attributes.values())
        orig_bonus = generatecharacter.bonus_check(original_class, attrs_list)
        dest_bonus = generatecharacter.bonus_check(destination, attrs_list)

        def _adj(raw, has_bonus):                                   # applies 10/11 if class has bonus, else identity
            return int(int(raw) * 10 / 11) if has_bonus else int(raw)
        orig_xp_floor = _adj(generatecharacter.return_xp(original_class)[transition_level - 1], orig_bonus)
        self.initiate_dual_class(destination, starting_xp=orig_xp_floor)

        # ---- Bard track: second transition (Thief → Bard) --------------------
        # Determine whether and at what Thief level the second transition fires.
        # The remaining XP budget after the first transition is used for the
        # Thief leg; we simulate level-ups within the Thief window (5–8).
        if is_bard_track and destination == 'Thief':
            thief_window = range(5, 9)          # levels 5, 6, 7, 8
            thief_transition_level = None
            for lvl in range(1, final_level + 1):
                if lvl not in thief_window:
                    continue
                # Last level in window (8) is always a guaranteed transition if eligible
                prob = 1.0 if lvl == thief_window[-1] else 0.50
                if random.random() < prob:
                    thief_transition_level = lvl
                    break
            if thief_transition_level is not None and sc.bard_eligible(self.attributes):
                thief_xp_floor = _adj(generatecharacter.return_xp('Thief')[thief_transition_level - 1],
                                      generatecharacter.bonus_check('Thief', attrs_list))
                combined_xp = orig_xp_floor + thief_xp_floor
                self.xp = combined_xp
                self.calculate_level(0, uncapped=True)
                if self.dual_class is not None and 'Thief' in self.classes:
                    # Bard gets whatever XP remains from the total pool after
                    # Fighter and Thief legs are consumed.
                    bard_dest_bonus = generatecharacter.bonus_check('Bard', attrs_list)
                    bard_xp_available = max(0, total_xp - combined_xp)
                    bard_xp_table = generatecharacter.return_xp('Bard')
                    # Walk the table to find the highest Bard level affordable.
                    # bard_xp_table[N-1] = XP floor of level N.
                    bard_target_level = 1
                    for bard_lvl in range(2, len(bard_xp_table)):
                        if bard_xp_available >= _adj(bard_xp_table[bard_lvl - 1], bard_dest_bonus):
                            bard_target_level = bard_lvl
                        else:
                            break
                    if bard_target_level >= 2:
                        bard_lvl_floor = _adj(bard_xp_table[bard_target_level - 1], bard_dest_bonus)
                        if bard_target_level < len(bard_xp_table) - 1:
                            bard_lvl_ceil = _adj(bard_xp_table[bard_target_level], bard_dest_bonus)
                        else:
                            bard_lvl_ceil = bard_lvl_floor + 1
                        bard_scatter = int((bard_lvl_ceil - bard_lvl_floor)
                                          * random.randint(1, 10) / 100)
                        self.initiate_dual_class('Bard', starting_xp=combined_xp)
                        self.xp = combined_xp + min(bard_lvl_floor + bard_scatter,
                                                    bard_lvl_ceil - 1)
                        self.calculate_level(0, uncapped=True)
                        self.display_class = 'Bard'
                        self.display_level = generatecharacter.display_level(self.level)
                        self.hp = self._flatten()
                        return

        # ---- Standard XP resolution (non-bard or bard track that didn't reach stage 3) ---
        # XP legs are independent. Destination is always single-class — no doubling.
        dest_xp_floor = _adj(generatecharacter.return_xp(destination)[final_level - 1], dest_bonus)
        dest_xp_ceil  = _adj(generatecharacter.return_xp(destination)[final_level], dest_bonus)
        dest_scatter  = int((dest_xp_ceil - dest_xp_floor) * random.randint(1, 10) / 100)
        dest_xp       = dest_xp_floor + dest_scatter
        # Clamp total XP so the character never resolves beyond final_level.
        self.xp = min(orig_xp_floor + dest_xp, orig_xp_floor + dest_xp_ceil - 1)
        self.calculate_level(0, uncapped=True)
        self.display_class = generatecharacter.display_classes(self.classes[:], self.dual_class)
        self.display_level = generatecharacter.display_level(self.level, self.dual_class)
        self.hp = self._flatten()

    def initiate_dual_class(self, destination: str, starting_xp: int = 1) -> None:
        # Bard second transition fires when post-crossover (two classes); all others require one class.
        is_bard_second = (destination == 'Bard'
                          and self.intended_class == 'Bard'
                          and self.dual_class is not None)
        if not is_bard_second and len(self.classes) != 1:
            raise ValueError("initiate_dual_class() requires exactly one active class.")
        original = self.classes[0]      # we freeze and capture hp and xp at the moment of transition

        # ---- Thief → Bard (second bard-track transition) ----------------------
        # The existing dual_class dict holds the frozen Fighter history from
        # stage 1.  We carry it forward into the new dict.
        if destination == 'Bard' and self.intended_class == 'Bard' and self.dual_class is not None:
            fighter_level = self.dual_class['original_level']          # Fighter level frozen at stage 1
            thief_level   = max(self.level)                            # Thief level at transition
            # Post-crossover layout: hp_history = [thief_rolls, fighter_rolls, [thief_con, fighter_con]]
            thief_rolls   = self.hp_history[0][:]                      # Thief destination rolls
            fighter_rolls = self.hp_history[1][:]                      # frozen Fighter rolls (already in hp_history)
            con_list      = self.hp_history[-1]                        # [thief_con, fighter_con]
            thief_con     = con_list[0]
            fighter_con   = con_list[1]
            self.dual_class = {
                'original':       'Thief',
                'destination':    'Bard',
                'original_level': thief_level,
                'original_hp':    [thief_rolls, fighter_rolls, [thief_con, fighter_con]],
                'fighter_level':  fighter_level,
                'intended_class': 'Bard',
                'frozen_xp':      self.xp,
            }
            # Bard starts at level 1; first roll is always 0 (accrual begins at 2nd level)
            self.xp, self.classes, self.level = starting_xp, ['Bard'], [1]
            self.hp_history = [
                [0],                                                   # Bard slot: level 1 = 0
                thief_rolls,                                           # frozen Thief rolls
                fighter_rolls,                                         # frozen Fighter rolls
                [0, thief_con, fighter_con],                           # con: Bard=0, Thief frozen, Fighter frozen
            ]
            self.hp = self._flatten()
            self.display_class = 'Bard'             # stage 3 displays as 'Bard' only — not 'Bard|Thief'
            self.display_level = generatecharacter.display_level(self.level)
            next_level_raw = generatecharacter.generate_level(
                self.attributes, self.classes, self.race, self.xp, self.excess).pop('next_level')
            self.next_level = [int(next_level_raw[0]), next_level_raw[1]]
            return

        # ---- Standard first dual-class transition -----------------------------
        self.dual_class = {'original': original, 'destination': destination, 'original_level': max(self.level),
                           'original_hp': [row[:] for row in self.hp_history], 'frozen_xp': self.xp}
        self.xp, self.classes, self.level = starting_xp, [destination], [1]     # destination becomes only class
        frozen_rolls = self.dual_class['original_hp'][:-1]                      # excludes old con list
        frozen_con   = self.dual_class['original_hp'][-1]                       # preserved original con bonuses
        # Con list: destination starts at 0 pre-crossover, original is frozen.
        self.hp_history = [[0], *frozen_rolls, [0] + frozen_con]
        self.hp = self._flatten()
        self.display_class = generatecharacter.display_classes(self.classes[:], self.dual_class)
        self.display_level = generatecharacter.display_level(self.level, self.dual_class)
        next_level_raw = generatecharacter.generate_level(self.attributes, self.classes, self.race, self.xp,
                                                          self.excess).pop('next_level')
        self.next_level = [int(next_level_raw[0]), next_level_raw[1]]   # computes next_level for destination class

    def _detect_crossover(self) -> bool:
        if self.dual_class is None:
            return False            # non-dual-class unit
        if 'fighter_level' in self.dual_class:
            return False            # stage-3 Bard: frozen classes never reinserted into self.classes
        if max(self.level) <= self.dual_class['original_level']:
            return False            # destination has not yet exceeded original level
        if self.dual_class['original'] in self.classes:
            return False            # already crossed over
        return True                 # destination level exceeds original_level: reinsertion needed

    def _apply_crossover(self) -> None:                             # reinserts original class and hp_history
        original, orig_level = self.dual_class['original'], self.dual_class['original_level']
        self.classes.append(original)                               # appends original class at its frozen level
        self.level.append(orig_level)
        dest_rolls = self.hp_history[0]                             # correct mix of zeros and non-zeroes
        frozen_rolls = self.dual_class['original_hp'][:-1]          # strip old con list
        self.hp_history = [dest_rolls, *frozen_rolls, [0, 0]]       # placeholder con list for _recompute
        self._recompute_dual_class_con()                            # both classes live from current Con
        self.hp = self._flatten()
        self.display_class = generatecharacter.display_classes(self.classes[:], self.dual_class)
        self.display_level = generatecharacter.display_level(self.level, self.dual_class)

    def _undo_dual_class(self) -> str:                              # reverses dual-class transition on drain to 0
        # Stage-3 Bard: revert to post-crossover Thief|Fighter, not bare Thief.
        # original_hp = [thief_rolls, fighter_rolls, [thief_con, fighter_con]]
        if 'fighter_level' in self.dual_class:
            thief_level   = self.dual_class['original_level']
            fighter_level = self.dual_class['fighter_level']
            thief_rolls   = self.dual_class['original_hp'][0]
            fighter_rolls = self.dual_class['original_hp'][1]
            frozen_con    = self.dual_class['original_hp'][2]       # [thief_con, fighter_con]
            self.classes  = ['Thief', 'Fighter']
            self.level    = [thief_level, fighter_level]
            self.hp_history = [thief_rolls, fighter_rolls, frozen_con]
            self.xp       = self.dual_class['frozen_xp']
            # Reconstruct the Thief|Fighter dual_class dict so post-crossover
            # state is fully coherent (Fighter was the original at stage 1).
            self.dual_class = {
                'original':       'Fighter',
                'destination':    'Thief',
                'original_level': fighter_level,
                'original_hp':    [fighter_rolls[:], [frozen_con[1]]],
                'frozen_xp':      self.dual_class['frozen_xp'],
            }
            self.hp = self._flatten()
            self.display_class = generatecharacter.display_classes(self.classes[:], self.dual_class)
            self.display_level = generatecharacter.display_level(self.level, self.dual_class)
            next_level_raw = generatecharacter.generate_level(
                self.attributes, self.classes, self.race, self.xp, self.excess).pop('next_level')
            self.next_level = [int(next_level_raw[0]), next_level_raw[1]]
            return '{} reverts to Thief {}|Fighter {}'.format(
                self.character_name, thief_level, fighter_level)

        original, original_level = self.dual_class['original'], self.dual_class['original_level']
        self.classes, self.level = [original], [original_level]
        self.hp_history = self.dual_class['original_hp']            # restored deep copy
        self.xp, self.dual_class = self.dual_class['frozen_xp'], None
        self.hp, self.display_class = self._flatten(), generatecharacter.display_classes(self.classes[:])
        self.display_level = generatecharacter.display_level(self.level)
        next_level_raw = generatecharacter.generate_level(
            self.attributes, self.classes, self.race, self.xp, self.excess).pop('next_level')
        self.next_level = [int(next_level_raw[0]), next_level_raw[1]]
        return '{} reverts to {} {}'.format(self.character_name, original, original_level)

    def calculate_level(self, adj=0, uncapped=False):           # adj is either -1 or 0 / also updates hit points
        pre_crossover = (self.dual_class is not None and self.dual_class['original'] not in self.classes)
        post_crossover = (self.dual_class is not None and self.dual_class['original'] in self.classes)
        if (pre_crossover or post_crossover) and adj < 0 and self.level[0] + adj < 1:
            return self._undo_dual_class()          # Dual-classed units drained to zero revert to origin class
        if not pre_crossover and not post_crossover and max(self.level) + adj < 1:      # normal wight guard
            return self.wightify()
        result = self._resolve_xp_and_level(adj, uncapped, post_crossover)
        if result is None:
            return ''                               # XP within current level band — no level change
        hp_calcs, number_of_classes, current_xp_floor, current_xp_ceiling = result
        message = self._rebuild_hp_rolls(hp_calcs, number_of_classes, current_xp_floor, current_xp_ceiling)
        self._rebuild_con_bonus(hp_calcs, number_of_classes)
        if "Ninja" in self.classes:                                 # ninjas require a special exception for con bonus
            for b in range(number_of_classes):
                self.hp_history[number_of_classes][b] *= 2
        self.hp = self._flatten()
        if 'Bard' in self.classes and self.dual_class is not None and 'fighter_level' in self.dual_class:
            self.display_class = 'Bard'
            self.display_level = generatecharacter.display_level(self.level)
        else:
            self.display_level = generatecharacter.display_level(self.level, self.dual_class)
        if self._detect_crossover():
            self._apply_crossover()
        return message

    def _resolve_xp_and_level(self, adj, uncapped, post_crossover):     # resolves xp, level and next_level
        if self.dual_class is not None:             # Dual-classed units earn XP as if single class (full xp)
            nxp_classes, nxp_levels = [self.classes[0]], [self.level[0]]
        else:
            nxp_classes, nxp_levels = self.classes, self.level
        current_xp_floor = max(generatecharacter.next_xp(nxp_classes, nxp_levels, self.attributes, -1))
        current_xp_ceiling = min(generatecharacter.next_xp(nxp_classes, nxp_levels, self.attributes))
        if adj < 0:                                             # if the adjustment is negative...
            if self.dual_class is not None:
                drain_levels = [self.level[0] + adj]            # destination level shifted by -1
                upper_thr = generatecharacter.next_xp(nxp_classes, drain_levels, self.attributes)[0]
                drain_levels[0] -= 1                            # one further for the lower bound
                lower_threshold = generatecharacter.next_xp(nxp_classes, drain_levels, self.attributes)[0]
            else:
                upper_thr = max(generatecharacter.next_xp(self.classes, self.level, self.attributes, adj))
                ind_pos = generatecharacter.next_xp(self.classes, self.level, self.attributes, adj).index(upper_thr)
                lower_threshold = generatecharacter.next_xp(self.classes, self.level, self.attributes, adj - 1)[ind_pos]
            self.xp = int((lower_threshold + upper_thr) / 2)    # ...sets xp to midpoint of destination level
        if current_xp_floor <= self.xp < current_xp_ceiling:
            return None                                         # no level change
        hp_calcs, number_of_classes = [], len(self.level)
        level_before = self.level[:]                            # snapshot pre-award level for cap check below
        for ch_cl in range(number_of_classes):                  # recalculates level(s) from scratch...
            self.level[ch_cl] = 0                               # ...and populates hp_calcs list
            hp_calcs.append(datalocus.call_hp(self.classes[ch_cl]))
        if self.dual_class is not None:     # if dual-class, pass a separate list and write the result after resolution
            xp_classes, xp_levels = [self.classes[0]], [self.level[0]]
        else:
            xp_classes, xp_levels = self.classes, self.level
        self.next_level = generatecharacter.increment_xp(xp_classes, xp_levels, self.xp, self.attributes)
        self.next_level[0] = int(self.next_level[0])            # increment_xp may return float from bonus adjustment
        if self.dual_class is not None:
            self.level[0] = xp_levels[0]                        # write resolved destination level back to self.level
        if post_crossover:                                      # clamps original class back to frozen level
            orig_idx = self.classes.index(self.dual_class['original'])
            self.level[orig_idx] = self.dual_class['original_level']
        if not uncapped and adj >= 0:                           # caps interactive level-ups at +1 per award_xp() call
            for ch_cl in range(number_of_classes):              # uncapped=True is only for bulk units
                if self.level[ch_cl] > level_before[ch_cl] + 1:     # if XP jumps more than 1 level, clamp to threshold
                    trim = generatecharacter.next_xp(xp_classes, level_before[:len(xp_classes)], self.attributes, 1)[0]
                    self.xp = int(trim) - 1                     # re-runs XP calc so level/next_level are consistent
                    for reset in range(len(xp_classes)):
                        xp_levels[reset] = 0
                    self.next_level = generatecharacter.increment_xp(
                        xp_classes, xp_levels, self.xp, self.attributes)
                    self.next_level[0] = int(self.next_level[0])
                    if self.dual_class is not None:
                        self.level[0] = xp_levels[0]            # write resolved level back after cap re-run
                    if post_crossover:
                        self.level[orig_idx] = self.dual_class['original_level']
                    break                                       # only one class can trigger per award
        return hp_calcs, number_of_classes, current_xp_floor, current_xp_ceiling

    def _rebuild_hp_rolls(self, hp_calcs, number_of_classes, current_xp_floor, current_xp_ceiling):
        message = ''
        is_bard = ('Bard' in self.classes
                   and self.dual_class is not None
                   and 'fighter_level' in self.dual_class)
        if self.xp < current_xp_floor:                          # if xp are lower than the current floor...
            for ch_cl in range(number_of_classes):              # ...trims off hp
                self.hp_history[ch_cl] = self.hp_history[ch_cl][0:self.level[ch_cl]]
                message = '{} lost one level!'.format(self.character_name)
        if self.xp >= current_xp_ceiling:                       # if xp are greater than the current ceiling...
            for ch_cl in range(number_of_classes):              # ...calculates additional hp
                if is_bard and self.classes[ch_cl] == 'Bard':
                    # Bard exception: accrual starts at 2nd level Bard (not post-crossover).
                    # Level 1 is always 0; rolls begin at level 2 regardless of original_level.
                    current_len = len(self.hp_history[ch_cl])
                    for slot in range(current_len, self.level[ch_cl]):
                        if slot == 0:                           # 1st level Bard: always zero
                            self.hp_history[ch_cl].append(0)
                        else:                                   # 2nd level onwards: real rolls
                            hitpoints.hp_compute_mid(hp_calcs[ch_cl], self.hp_history[ch_cl],
                                                     slot + 1, len(self.hp_history[ch_cl]))
                            hitpoints.hp_compute_top(hp_calcs[ch_cl], self.hp_history[ch_cl], slot + 1)
                elif (self.dual_class is not None               # pre-crossover destination accumulates zeros
                        and self.classes[ch_cl] == self.dual_class['destination']):
                    orig_level = self.dual_class['original_level']
                    current_len = len(self.hp_history[ch_cl])
                    for slot in range(current_len, self.level[ch_cl]):
                        if slot < orig_level:                   # slot is 0-indexed; slot 0 = level 1
                            self.hp_history[ch_cl].append(0)   # pre-crossover: always zero
                        else:
                            hitpoints.hp_compute_mid(hp_calcs[ch_cl], self.hp_history[ch_cl],
                                                     slot + 1, len(self.hp_history[ch_cl]))
                            hitpoints.hp_compute_top(hp_calcs[ch_cl], self.hp_history[ch_cl], slot + 1)
                else:
                    hitpoints.hp_compute_mid(hp_calcs[ch_cl], self.hp_history[ch_cl], self.level[ch_cl],
                                             len(self.hp_history[ch_cl]))
                    hitpoints.hp_compute_top(hp_calcs[ch_cl], self.hp_history[ch_cl], self.level[ch_cl])
                message = '{} leveled up!'.format(self.character_name)
        return message

    def _rebuild_con_bonus(self, hp_calcs, number_of_classes):      # reattaches and recalculates trailing con bonus
        is_bard = ('Bard' in self.classes
                   and self.dual_class is not None
                   and 'fighter_level' in self.dual_class)
        if is_bard:
            # Bard stage 3: hp_history = [bard_rolls, thief_rolls, fighter_rolls, con_list]
            # Preserve the three roll lists and recompute the con list.
            existing_con = self.hp_history[-1]
            bard_rolls   = self.hp_history[0]
            thief_rolls  = self.dual_class['original_hp'][0]
            fighter_rolls = self.dual_class['original_hp'][1]
            self.hp_history = [bard_rolls, thief_rolls, fighter_rolls, existing_con]
            self._recompute_bard_con()
        elif self.dual_class is not None and self.dual_class['original'] not in self.classes:  # pre-crossover
            frozen_rolls = self.dual_class['original_hp'][:-1]                                 # strips old con list
            self.hp_history = [self.hp_history[0]] + frozen_rolls + [self.hp_history[-1]]
            self._recompute_dual_class_con()
        elif self.dual_class is not None:                                                      # post-crossover
            existing_con = self.hp_history[-1]
            self.hp_history = self.hp_history[0:number_of_classes] + [existing_con]
            self._recompute_dual_class_con()
        else:                                                                                  # standard path
            self.hp_history = self.hp_history[0:number_of_classes]
            hitpoints.con_bonus(self.hp_history, hp_calcs, self.attributes['Con'])

    def calculate_ac(self):                                 # calculates AC from dex_multiplier() and class_ac()
        if hasattr(self, 'ac'):                             # mob units: ac set directly, skip calculation
            return self.ac - 10                             # display is 10 + calculate_ac(), so AC 5 → returns -5
        dex_ac, class_defense = datalocus.dex_acbonus(self.attributes['Dex']) * self.dex_multiplier(), 0
        if "Monk" in self.classes or "Oriental Monk" in self.classes or "Kensai" in self.classes:
            class_defense = datalocus.class_ac(tuple(self.classes), tuple(self.level))
        final = dex_ac - class_defense
        return final

    def dex_multiplier(self):                               # this is strictly for monks (x0) and barbs (x2)
        multiplier = datalocus.dex_acmultiplier(tuple(self.classes))
        return multiplier

    def str_damage_bonus(self):                             # calculates damage bonus from str
        display, multiplier = self.display_strength(), self.str_multiplier()
        bonus = datalocus.str_damagebonus(self.attributes['Str'], self.attributes['Exc'], display, multiplier)
        return bonus

    def str_multiplier(self):
        multiplier = datalocus.str_multiplier(tuple(self.classes))
        return multiplier

    def class_thaco(self):                                  # returns class and level modifier for thaco
        if self.dual_class is not None and max(self.level) > self.dual_class['original_level']:
            # post-crossover: include frozen original class at its frozen level
            classes = tuple(self.classes) + (self.dual_class['original'],)
            levels  = tuple(self.level)   + (self.dual_class['original_level'],)
        else:
            classes = tuple(self.classes)
            levels  = tuple(self.level)
        # Bard stage 3: also consider Fighter at its terminal level
        if ('Bard' in self.classes
                and self.dual_class is not None
                and 'fighter_level' in self.dual_class):
            classes += ('Fighter',)
            levels  += (self.dual_class['fighter_level'],)
        thaco = datalocus.base_thaco(classes, levels)
        return thaco                                        # (tuple['Fighter', 'Thief'], tuple[3, 4]) returns a 2

    def calculate_thaco(self):                              # combines class and strength modifiers
        if hasattr(self, 'thac0'):                          # mob units: thac0 set directly, skip calculation
            return self.thac0 - 20                          # display = 20 + calculate_thaco(), so THAC0 15 returns -5
        display, multiplier = self.display_strength(), self.str_multiplier()
        bonus = datalocus.str_thacobonus(self.attributes['Str'], self.attributes['Exc'], display, multiplier)
        final = -(self.class_thaco() + bonus)
        return final

    def class_movement(self):                               # calculates movement for non-armored characters
        if hasattr(self, 'movement'):
            return self.movement
        else:
            result = datalocus.race_class_movement(self.race, tuple(self.classes))      # race modifier & transpose
            class_modifier = datalocus.class_level_movement(tuple(self.level), tuple(result[1]))    # level modifier
            mv_rate = int(0.5 + (result[0][self.gender == 'female'] * class_modifier / 12))
            return mv_rate                                      # returned value is a rounded race_mod * class_mod

    def __getstate__(self):                          # strip event_bus before pickling (holds tkinter references)
        state = self.__dict__.copy()
        state['event_bus'] = None
        return state

    def __setstate__(self, state):                   # restore from pickle; event_bus left None — caller re-injects
        self.__dict__.update(state)

    def calculate_alignment(self):
        result = datalocus.race_class_alignment(self.race, tuple(self.classes))
        alignment = charalign.get_random_weighted_alignment(result[0], result[1])
        return alignment



# some_dude = Character(level=5, race="Halfling", classes=['Fighter', 'Thief'],
#                       attrib_list=[{'Str': 1, 'Int': 13, 'Wis': 9, 'Dex': 15, 'Con': 18, 'Cha': 11, 'Com': 4},
#                                    {'Str': 0, 'Int': 0, 'Wis': 0, 'Dex': 0, 'Con': 0, 'Cha': 0, 'Com': 0}])
# print(some_dude.__dict__)
#   output fields as of 11/6/22
#                   'character_name':   '',
#                   'race':             'Halfling',
#                   'classes':          ['Fighter', 'Thief']
#                   'display_class':    'display_class': 'Fighter/Thief',
#                   'attributes':       {'Str': 15, 'Int': 13, 'Wis': 9, 'Dex': 15, 'Con': 19, 'Cha': 11, 'Com': 4},
#                   'excess':           {'Str': 0, 'Int': 0, 'Wis': 0, 'Dex': 0, 'Con': 0, 'Cha': 0, 'Com': 0},
#                   'gender':           'male'
#                   'age':              [54, 'mature', '68', {'Str': 1, 'Int': 0, 'Wis': 0, 'Dex': 0, 'Con': 1, \
#                                       'Cha': 0, 'Com': 0, 'Exc': 0}, 143],
#                   'xp':               20135,
#                   'level':            [4, 5],
#                   'display_level':    '4/5',
#                   'next_level':       [36000, 'Fighter'],
#                   'hp':               36
#                   'hp_history':       [[10, 6, 2, 1], [5, 1, 4, 6, 6], [20, 10]],
#                   'size':             [33, 59]


# ident = {}
# for a in range(10):
#     temp = 'p' + str(a+1).zfill(2)
#     ident[temp] = temp
#     ident[temp] = Character(7)
#     # ident[temp].modify_age(5)
#     ident[temp].display_attributes()
#     ident[temp].class_movement()
    # print(ident[temp].calculate_ac())
    # if ident[temp][]
    # print(ident[temp].__dict__, "\n")
    # ident[temp].modify_xp(10000)
    # ident[temp].calculate_level(0)
    # ident[temp].display_attributes()

# print('p01')
# print(list(ident.keys()))
# print(ident['p01'].hp)

    # ident[a].modify_age(1)
    # print(ident[a].__dict__)
    # ident[a].modify_attribute('Cha', +4)
    # print(ident[a].excess["Str"])

# print(ident[2].__dict__)
# print(p2.__dict__)