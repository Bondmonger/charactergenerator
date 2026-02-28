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
    CHARACTER_RENAMED, XP_AWARDED, LEVEL_CHANGED = \
        "character_renamed", "xp_awarded", "level_changed"
    ATTRIBUTE_CHANGED, AGE_CHANGED, CHARACTER_TRANSFORMED = \
        "attribute_changed", "age_changed", "character_transformed"


def roll(b):  # rolls a single die of "b" sides
    return random.randrange(1, b + 1)


class Character:
    def __init__(self, level=1, race='', gender='random', classes=(), attrib_list=(), event_bus=None,
                 auto_dual_class=False):
        # start = time.time()
        self.event_bus = event_bus                      # optional EventBus for domain event emission
        self.dual_class = None                          # populated at transition; see brief for schema
        self.character_name = ''
        # print("classes: ", classes)
        self.race = selectclass.race_from_class(classes) if len(race) == 0 else race            # 'Gray Elf'
        self.classes = selectclass.random_class(self.race) if len(classes) == 0 else classes    # ['Fighter', 'Thief']
        self.alignment = self.calculate_alignment()
        # end = time.time()
        # print('character generation duration:', end - start)
        self.attributes = attributes.methodvi(self.race, self.classes) if len(attrib_list) == 0 else attrib_list
        # [{'Str': 14, 'Int': 13, ...
        self.excess, self.attributes = self.attributes.pop(1), self.attributes[0]   # excess = same format as attributes
        self.gender = heightweight.random_gender() if gender == "random" else gender            # female
        # attribs zipper: attributes.apply_race_modifiers('Grugach', [20, 12, 12, 12, 12, 12, 12])
        #                  ^^^ applies racial modifier and returns an excess dict
        # class_string converter: selectclass.string_to_list('Fighter/Thief', '/')
        if self.classes[0] == '0-level':    # these units throw an error when AC/THAC0/movement are calculated
            self.age = agevalues.generate_age(self.race, classes, level)
            self.display_class, self.xp, self.level, self.hp = '0-level', 0, [0], 5
            self.size = heightweight.size(self.race, self.gender)
            return
        self.age = agevalues.generate_age(self.race, self.classes, level)
        for k, v in self.attributes.items():
            self.attributes[k] = self.attributes[k] + self.age[3][k]
        self.display_class = generatecharacter.display_classes(self.classes)
        self.xp = generatecharacter.pc_xp(level)                                    # generates xp from mean
        self.level = generatecharacter.generate_level(self.attributes, self.classes, self.race, self.xp, self.excess)
        self.level, self.next_level = self.level['level'], self.level.pop('next_level')
        self.display_level = generatecharacter.display_level(self.level)
        self.hp_history = hitpoints.generate_hp(self.classes, self.level, self.attributes['Con'])
        self.modify_age(0)  # this is to factor in modifiers from the age increments in generate_level()
        self.size = heightweight.size(self.race, self.gender)
        self.hp = generatecharacter.flatten(self.hp_history)
        if auto_dual_class:
            self._apply_auto_dual_class(max(self.level))
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
        con_posit = len(self.classes)
        self.hp_history[con_posit] = hitpoints.generate_hp(self.classes, self.level, self.attributes['Con'])[con_posit]
        self.hp = generatecharacter.flatten(self.hp_history)
        return

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
        self.next_level = generatecharacter.generate_level(self.attributes, self.classes, self.race, self.xp,
                                                           self.excess).pop('next_level')
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

    def _apply_auto_dual_class(self, final_level: int) -> None:
        """Retroactively apply probabilistic dual-class transition for bulk /
        automated character generation.

        Called from __init__ after the character is fully constructed at
        `final_level`.  Walks levels 1..final_level on the original class,
        rolling dual_class_transition_prob() at each.  On a hit, picks a
        random destination from dual_class_options(), calls
        initiate_dual_class(), then distributes the remaining XP to the
        destination class via calculate_level().

        Only fires for single-class characters — eligibility rules are
        enforced inside dual_class_options().
        """
        if len(self.classes) != 1:
            return
        import selectclass as sc
        original_class = self.classes[0]
        transition_level = None
        for lvl in range(1, final_level + 1):
            prob = sc.dual_class_transition_prob(original_class, lvl)
            if prob > 0 and random.random() < prob:
                transition_level = lvl
                break                           # first hit wins
        if transition_level is None:
            return
        options = sc.dual_class_options(original_class, self.attributes,
                                        self.alignment, self.race)
        if not options:
            return
        destination = random.choice(options)
        # Rebuild character state to exactly the transition point so that
        # initiate_dual_class() freezes the right HP history.
        self.level       = [transition_level]
        self.hp_history  = hitpoints.generate_hp(
            [original_class], [transition_level], self.attributes['Con'])
        # Set XP to midpoint of the transition level for the original class
        orig_xp_floor    = int(generatecharacter.return_xp(original_class)[transition_level - 1])
        orig_xp_ceil     = int(generatecharacter.return_xp(original_class)[transition_level])
        self.xp          = (orig_xp_floor + orig_xp_ceil) // 2
        self.initiate_dual_class(destination)
        # Award XP appropriate for the requested final_level so the destination
        # class levels up — use pc_xp(final_level) as the target total
        target_xp        = generatecharacter.pc_xp(final_level)
        if target_xp > self.xp:
            self.xp      = target_xp
            self.calculate_level(0)
        self.display_class = generatecharacter.display_classes(self.classes[:])
        self.display_level = generatecharacter.display_level(self.level)
        self.hp            = generatecharacter.flatten(self.hp_history)

    def initiate_dual_class(self, destination: str) -> None:
        """Freeze the current (single) class and start the dual-class
        transition.  Must be called while the character is still single-
        class (len(self.classes) == 1).

        After this call:
          self.dual_class  = populated schema dict
          self.classes     = [destination]          (active class only)
          self.level       = [0]                    (destination starts at 0)
          self.hp_history  = [[0], frozen_rolls, [0]]
                              ^dest zeros  ^original hp  ^con placeholder
        """
        if len(self.classes) != 1:
            raise ValueError("initiate_dual_class() requires exactly one active class.")
        original = self.classes[0]
        self.dual_class = {
            'original':       original,
            'destination':    destination,
            'original_level': max(self.level),
            'original_hp':    [row[:] for row in self.hp_history],  # deep copy
        }
        # Transition: destination becomes the only active class, level 0
        self.classes     = [destination]
        self.level       = [0]
        # hp_history: [dest_zeros, frozen_original_rolls, con_placeholder]
        frozen_rolls = self.dual_class['original_hp'][:-1]  # exclude old con list
        self.hp_history  = [[0], *frozen_rolls, [0]]
        self.hp          = generatecharacter.flatten(self.hp_history)
        self.display_class  = destination
        self.display_level  = '0'

    def _detect_crossover(self) -> bool:
        """Return True if the destination level has just exceeded original_level
        (i.e. we are at the first tick past crossover).  Triggers class
        reinsertion into self.classes and real HP rolls for the destination.

        Display order: [destination, original]  — active/original ordering.
        (Pending community sign-off; see open question #1 in project brief.)
        """
        if self.dual_class is None:
            return False
        if max(self.level) <= self.dual_class['original_level']:
            return False
        # Already crossed over if original is already back in classes
        if self.dual_class['original'] in self.classes:
            return False
        return True

    def _apply_crossover(self) -> None:
        """Reinsert the original class into classes and hp_history at crossover.

        Before: self.classes = ['Fighter'], self.hp_history = [[0,0,0,0,0,X], frozen, [con]]
        After:  self.classes = ['Fighter','Thief'], hp_history = [[real rolls], frozen, [con]]

        The zeros accumulated pre-crossover are replaced with real rolls
        via hp_compute_mid / hp_compute_top.
        """
        original      = self.dual_class['original']
        orig_level    = self.dual_class['original_level']
        dest_level    = self.level[0]
        dest_class    = self.classes[0]

        # Append original class at its frozen level
        self.classes.append(original)
        self.level.append(orig_level)

        # Build real HP rolls for destination from scratch
        dest_hpcalcs  = datalocus.call_hp(dest_class)
        dest_rolls    = [hitpoints.hp_compute_first(dest_hpcalcs)]
        hitpoints.hp_compute_mid(dest_hpcalcs, dest_rolls, dest_level, 1)
        hitpoints.hp_compute_top(dest_hpcalcs, dest_rolls, dest_level)

        # Reconstruct hp_history: [dest_real_rolls, frozen_orig_rolls, con_list]
        frozen_rolls = self.dual_class['original_hp'][:-1]   # strip old con list
        self.hp_history = [dest_rolls, *frozen_rolls]
        # Recompute con bonus across both classes
        hp_calcs_all = [datalocus.call_hp(c) for c in self.classes]
        hitpoints.con_bonus(self.hp_history, hp_calcs_all, self.attributes['Con'])
        self.hp = generatecharacter.flatten(self.hp_history)
        self.display_class  = generatecharacter.display_classes(self.classes[:])
        self.display_level  = generatecharacter.display_level(self.level)

    def calculate_level(self, adj=0):                           # adj is either -1 or 0 / also updates hit points
        # Pre-crossover destination is legitimately at level 0 — do not wightify.
        # Only wightify when a fully-levelled character is drained below level 1.
        pre_crossover = (self.dual_class is not None
                         and self.dual_class['original'] not in self.classes)
        if not pre_crossover and max(self.level) + adj < 1:    # 1st level energy drain → wight
            return self.wightify()
        message = ''
        # next_xp(diff=-1) reads xp_table[level-1]; level 0 → index -1 (wraps to end of list).
        # Guard: if any class is at level 0 (pre-crossover destination), the XP floor is 0.
        if min(self.level) == 0:
            current_xp_floor = 0
        else:
            current_xp_floor = max(generatecharacter.next_xp(self.classes, self.level, self.attributes, -1))
        current_xp_ceiling = min(generatecharacter.next_xp(self.classes, self.level, self.attributes))
        if adj < 0:                                             # if the adjustment is negative...
            upper_thr = max(generatecharacter.next_xp(self.classes, self.level, self.attributes, adj))
            ind_pos = generatecharacter.next_xp(self.classes, self.level, self.attributes, adj).index(upper_thr)
            lower_threshold = generatecharacter.next_xp(self.classes, self.level, self.attributes, adj - 1)[ind_pos]
            self.xp = int((lower_threshold + upper_thr) / 2)    # ...sets xp to midpoint of destination level
        if current_xp_floor <= self.xp < current_xp_ceiling:
            return ''                                           # returns an empty string if no level change
        hp_calcs, number_of_classes = [], len(self.level)
        # The one-level cap prevents skipping levels on normal characters.
        # Pre-crossover dual-class: the destination starts at 0 and must be
        # allowed to jump to wherever the accumulated XP actually puts it.
        if not pre_crossover:
            if self.xp >= min(generatecharacter.next_xp(self.classes, self.level, self.attributes, 1)):  # caps level-up
                self.xp = min(generatecharacter.next_xp(self.classes, self.level, self.attributes, 1)) - 1
        for ch_cl in range(number_of_classes):                  # recalculates level(s) from scratch...
            self.level[ch_cl] = 0                               # ...and populates hp_calcs list
            hp_calcs.append(datalocus.call_hp(self.classes[ch_cl]))
        self.next_level = generatecharacter.increment_xp(self.classes, self.level, self.xp, self.attributes)
        if self.xp < current_xp_floor:                          # if xp are lower than the current floor...
            for ch_cl in range(number_of_classes):              # ...trims off hp
                self.hp_history[ch_cl] = self.hp_history[ch_cl][0:self.level[ch_cl]]
                message = '{} lost one level!'.format(self.character_name)
        if self.xp >= current_xp_ceiling:                       # if xp are greater than the current ceiling...
            for ch_cl in range(number_of_classes):              # ...calculates additional hp
                # Pre-crossover dual-class: destination class accumulates zeros, not real rolls
                if (self.dual_class is not None
                        and max(self.level) <= self.dual_class['original_level']
                        and self.classes[ch_cl] == self.dual_class['destination']):
                    new_entries = self.level[ch_cl] - len(self.hp_history[ch_cl])
                    self.hp_history[ch_cl].extend([0] * max(0, new_entries))
                else:
                    hitpoints.hp_compute_mid(hp_calcs[ch_cl], self.hp_history[ch_cl], self.level[ch_cl],
                                             len(self.hp_history[ch_cl]))
                    hitpoints.hp_compute_top(hp_calcs[ch_cl], self.hp_history[ch_cl], self.level[ch_cl])
                message = '{} leveled up!'.format(self.character_name)
        # Trim hp_history to active classes only — but pre-crossover, frozen original
        # rolls live between the destination slot and the con list; preserve them.
        if self.dual_class is not None and self.dual_class['original'] not in self.classes:
            # Pre-crossover: layout is [dest_rolls, *frozen_rolls, con_list]
            # Keep destination slot + frozen rolls; rebuild con with destination hp_calcs only.
            frozen_rolls = self.dual_class['original_hp'][:-1]   # strip old con list
            self.hp_history = [self.hp_history[0]] + frozen_rolls
            hitpoints.con_bonus(self.hp_history, hp_calcs, self.attributes['Con'])
        else:
            self.hp_history = self.hp_history[0:number_of_classes]  # standard path
            hitpoints.con_bonus(self.hp_history, hp_calcs, self.attributes['Con'])
        if "Ninja" in self.classes:                             # ninjas require a special exception for con bonus
            for b in range(number_of_classes):
                self.hp_history[number_of_classes][b] *= 2
        self.hp = generatecharacter.flatten(self.hp_history)
        self.display_level = generatecharacter.display_level(self.level)
        if self._detect_crossover():
            self._apply_crossover()
        return message

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
        thaco = datalocus.base_thaco(classes, levels)
        return thaco                                        # (tuple['Fighter', 'Thief'], tuple[3, 4]) returns a 2

    def calculate_thaco(self):                              # combines class and strength modifiers
        if hasattr(self, 'thac0'):                          # mob units: thac0 set directly, skip calculation
            return self.thac0 - 20                          # display is 20 + calculate_thaco(), so THAC0 15 → returns -5
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
