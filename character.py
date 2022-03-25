import csv
import random
import attributes
import hitpoints
import agevalues
import heightweight
import generatecharacter
import selectclass


def roll(b):  # rolls a single die of "b" sides
    return random.randrange(1, b + 1)


class Character:
    def __init__(self, level=1, race='', gender='random', classes=(), attrib_list=()):
        self.character_name = ''

        if len(race) == 0:
            self.race = selectclass.random_race()                                   # 'Gray Elf'
        else:
            self.race = race

        if len(classes) == 0:
            self.classes = selectclass.random_class(self.race)                      # ['Fighter', 'Thief']
        else:
            self.classes = classes

        if len(attrib_list) == 0:
            self.attributes = attributes.methodvi(self.race, self.classes)          # [{'Str': 14, 'Int': 13, ...
        else:
            self.attributes = attrib_list

        self.excess, self.attributes = self.attributes.pop(1), self.attributes[0]   # excess = same format as attributes

        if gender == "random":
            self.gender = heightweight.random_gender()                              # 'female'
        else:
            self.gender = gender

        # attribs zipper: attributes.apply_race_modifiers('Grugach', [20, 12, 12, 12, 12, 12, 12])
        #                  ^^^ applies racial modifier and returns an excess dict
        # class_string converter: selectclass.string_to_list('Fighter/Thief', '/')
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
        return

    def display_strength(self):                                     # calculates a displayable strength
        archetypes = []
        for character_class in self.classes:
            archetypes.append(attributes.archetype(character_class))
        if self.attributes['Str'] == 18 and self.attributes['Exc'] > 0 and "Fighter" in archetypes:
            displaystr = str(self.attributes['Str']) + '/' + str(self.attributes['Exc'])[-2:].zfill(2)
        else:
            displaystr = str(self.attributes['Str'])
        return displaystr

    # not currently in use, previously included in update_charsheet via self.selected_character.display_attributes()
    def display_attributes(self):                                   # displays attributes in terminal
        print("{} {} {} {} --- hp: {} | hgt: {}'{}” wgt: {} lbs  age: {} ({}) --- str: {}, int {}, wis {}, dex {}, "
              "con {}, cha {}".format(generatecharacter.display_level(self.level), self.gender, self.race,
                                      self.display_class, str(self.hp), str(self.size[0] / 12)[0:1],
                                      str(self.size[0] % 12), str(self.size[1]), str(self.age[0]), self.age[1],
                                      self.display_strength(), str(self.attributes['Int']), str(self.attributes['Wis']),
                                      str(self.attributes['Dex']), str(self.attributes['Con']),
                                      str(self.attributes['Cha'])))
        return

    def modify_str(self, adjustment):
        max_strength = attributes.racial_maximums(self.race)[0]     # used at the end
        self.attributes['Str'] += adjustment
        if self.attributes['Str'] > 17:
            max_racial_str = attributes.exceptional_str(self.race)
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
        max_constitution = attributes.racial_maximums(self.race)[4]
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

    def modify_other_att(self, adjustment, attribute):
        ord_attrs = ['Str', 'Int', 'Wis', 'Dex', 'Con', 'Cha', 'Com']
        max_att = attributes.racial_maximums(self.race)[ord_attrs.index(attribute)]     # racial max by attr index pos.
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
        if attr == 'Wis':                           # because it is uncapped (unlike the other stats)
            self.modify_wis(adjustment)
        if attr in ['Int', 'Dex', 'Cha', 'Com']:    # no special considerations
            self.modify_other_att(adjustment, attr)
        self.calculate_level()
        self.next_level = generatecharacter.generate_level(self.attributes, self.classes, self.race, self.xp,
                                                           self.excess).pop('next_level')
        return

    def modify_age(self, adjustment):
        starting_category, starting_atts, atts_mod = self.age[1], [], []
        ord_attrs = ['Str', 'Int', 'Wis', 'Dex', 'Con', 'Cha', 'Com']
        self.age[0] += adjustment                                   # updates age number
        self.age[1] = agevalues.age_cat(self.race, self.age[0])[0]  # updates age category
        if starting_category != self.age[1]:
            for attrs in range(7):
                starting_atts.append(agevalues.age_adj(starting_category)[attrs])
                atts_mod.append(agevalues.age_adj(self.age[1])[attrs] - starting_atts[attrs])
            attrs_mod_dict = dict(zip(ord_attrs, atts_mod))
            for k, v in attrs_mod_dict.items():
                self.modify_attribute(k, v)
            if self.age[0] > self.age[4]:
                self.age[1] = "dead"
        return

    def modify_xp(self, adjustment):
        if self.xp + adjustment >= int(generatecharacter.impending_mean_xp(self.xp)):
            self.modify_age(1)
        self.xp += adjustment
        return

    def wightify(self):
        self.hp = 3
        for a in range(4):
            self.hp += roll(8)
        self.race, self.classes, self.next_level, self.display_level = '', ['0-level'], [0, 'Wight'], ''
        self.display_class, self.age[1], self.xp = 'Wight', 'undead', 0
        self.attributes['Str'], self.attributes['Dex'], self.attributes['Con'], self.attributes['Com'] = 10, 10, 10, 10
        pass

    def calculate_level(self, adj=0):                           # also updates hit points
        if max(self.level) + adj < 1:                           # 1st level energy drain targets become wights
            self.wightify()
            message = "This character has become a WIGHT!"
            return message
        message = ''
        current_xp_floor = max(generatecharacter.next_xp(self.classes, self.level, self.attributes, -1))
        current_xp_ceiling = min(generatecharacter.next_xp(self.classes, self.level, self.attributes))
        if adj < 0:                                             # if the adjustment is negative...
            upper_thr = max(generatecharacter.next_xp(self.classes, self.level, self.attributes, adj))
            ind_pos = generatecharacter.next_xp(self.classes, self.level, self.attributes, adj).index(upper_thr)
            lower_threshold = generatecharacter.next_xp(self.classes, self.level, self.attributes, adj - 1)[ind_pos]
            self.xp = int((lower_threshold + upper_thr) / 2)    # ...sets xp to midpoint of destination level
        if current_xp_floor <= self.xp < current_xp_ceiling:
            return
        hp_calcs, number_of_classes = [], len(self.level)
        if self.xp >= min(generatecharacter.next_xp(self.classes, self.level, self.attributes, 1)):  # caps level-up
            self.xp = min(generatecharacter.next_xp(self.classes, self.level, self.attributes, 1)) - 1
        for ch_cl in range(number_of_classes):                  # recalculates level(s) from scratch...
            self.level[ch_cl] = 0                               # ...and populates hp_calcs list
            hp_calcs.append(hitpoints.call_hp(self.classes[ch_cl]))
        self.next_level = generatecharacter.increment_xp(self.classes, self.level, self.xp, self.attributes)
        if self.xp < current_xp_floor:                          # if xp are lower than the current floor...
            for ch_cl in range(number_of_classes):              # ...trims off hp
                self.hp_history[ch_cl] = self.hp_history[ch_cl][0:self.level[ch_cl]]
                message = '{} lost one level!'.format(self.character_name)
        if self.xp >= current_xp_ceiling:                       # if xp are greater than the current ceiling...
            for ch_cl in range(number_of_classes):              # ...calculates additional hp
                hitpoints.hp_compute_mid(hp_calcs[ch_cl], self.hp_history[ch_cl], self.level[ch_cl],
                                         len(self.hp_history[ch_cl]))
                hitpoints.hp_compute_top(hp_calcs[ch_cl], self.hp_history[ch_cl], self.level[ch_cl])
                message = '{} leveled up!'.format(self.character_name)
        self.hp_history = self.hp_history[0:number_of_classes]  # recalculates con bonus from scratch
        hitpoints.con_bonus(self.hp_history, hp_calcs, self.attributes['Con'])
        if "Ninja" in self.classes:                             # ninjas require a special exception for con bonus
            for b in range(number_of_classes):
                self.hp_history[number_of_classes][b] *= 2
        self.hp = generatecharacter.flatten(self.hp_history)
        self.display_level = generatecharacter.display_level(self.level)
        return message

    def calculate_ac(self):                                 # calculates AC from dex_multiplier() and class_ac()
        with open('attributevalues.csv') as dexbonus:
            for row in csv.reader(dexbonus):
                if str(self.attributes['Dex']) == row[0]:
                    dex_ac = int(row[22]) * self.dex_multiplier()
        final = dex_ac - self.class_ac()
        return final

    def calculate_thaco(self):                                 # calculates to-hit from str
        str_th = 0
        if len(self.display_strength()) > 2:                   # first checks for exceptional str
            with open('excstr.csv') as excbonus:
                for row in csv.reader(excbonus):
                    if self.attributes['Exc'] > int(row[0]):
                        str_th = (row[1]) * self.str_multiplier()
        else:                                                   # ...then calculates for non-exceptional str
            with open('attributevalues.csv') as strbonus:
                for line in csv.reader(strbonus):
                    if self.attributes['Str'] == int(line[0]):
                        str_th = int(line[1]) * self.str_multiplier()
        final = -(int(str_th) + self.class_thaco())
        return final

    def str_damage_bonus(self):                                # calculates damage bonus from str
        str_dmg = 0
        if len(self.display_strength()) > 2:                   # first checks for exceptional str
            with open('excstr.csv') as excbonus:
                for row in csv.reader(excbonus):
                    if self.attributes['Exc'] > int(row[0]):
                        str_dmg = (row[2]) * self.str_multiplier()
        else:                                                   # ...then calculates for non-exceptional str
            with open('attributevalues.csv') as strbonus:
                for line in csv.reader(strbonus):
                    if self.attributes['Str'] == int(line[0]):
                        str_dmg = int(line[2]) * self.str_multiplier()
        return str_dmg

    def dex_multiplier(self):
        result, final = [], 1
        with open('xpvalues.csv') as character_classes:
            for row in csv.reader(character_classes):
                for a in range(len(self.classes)):
                    if self.classes[a] == row[0]:
                        result.append(int(row[48]))
        for a in result:                                    # calculates a product of the dex multipliers
            final = final * a                               # monks are 0x, barbarians are 2x, all others are 1x
        return final

    def str_multiplier(self):
        result, final = [], 1
        with open('xpvalues.csv') as character_classes:
            for row in csv.reader(character_classes):
                for a in range(len(self.classes)):
                    if self.classes[a] == row[0]:
                        result.append(int(row[49]))
        for a in result:                                    # calculates a product of the str multipliers
            final = final * a                               # monks are 0x, all others are 1x
        return final

    def class_ac(self):                                     # calculates AC bonuses for non-armored characters
        result, final = [], []
        for a in range(len(self.classes)):                  # first it returns a 'transposition' value for each class
            with open('attributemins.csv') as ac_trans:
                for row in csv.reader(ac_trans):            # basically a 1 for kensai, 2 for monks, 0 for all others
                    if self.classes[a] == row[0]:
                        result.append(int(row[76]))
        for b in range(len(self.classes)):                  # then it compares those values...
            with open('levelvalues.csv') as ac_classmods:
                for row_lvl in csv.reader(ac_classmods):
                    if self.level[b] == int(row_lvl[0]):    # ...against class level to return an AC bonus
                        final.append(int(row_lvl[1+result[b]]))
        return max(final)

    def class_thaco(self):                                  # calculates thac0
        result, final = [], []
        for archetype in range(len(self.classes)):          # first it returns a 'transposition' value by archetype
            with open('xpvalues.csv') as th_trans:
                for row in csv.reader(th_trans):            # 0 for F, 1 for C, 2 for T and 3 for M
                    if self.classes[archetype] == row[0]:
                        result.append(int(row[51]))
        for b in range(len(self.classes)):                  # then it compares those values...
            with open('levelvalues.csv') as thaco_mod:
                for row_lvl in csv.reader(thaco_mod):
                    if self.level[b] == int(row_lvl[0]):    # ...against class level to return a thac0 bonus
                        final.append(int(row_lvl[5+result[b]]))
        return max(final)

    def class_movement(self):                               # calculates movement for non-armored characters
        result, final = [[], []], []
        with open('attributemins.csv') as movement_rates:   # generates a modifier list, [[12, 12], [0]]
            for row in csv.reader(movement_rates):
                if self.race == row[0]:
                    for male_female in range(2):            # ...populates racial movement [12, 12], for [male, female]
                        result[0].append(int(row[77+male_female]))
                for char_class in range(len(self.classes)):
                    if self.classes[char_class] == row[0]:  # ...populates class transp. mods (1 for monk, 2 for barb)
                        result[1].append(int(row[79]))
        for b in range(len(self.classes)):                  # then it compares those values...
            with open('levelvalues.csv') as move_mods:
                for row_lvl in csv.reader(move_mods):
                    if self.level[b] == int(row_lvl[0]):    # ...against class level to calculate movement
                        final.append(int(row_lvl[10+result[1][b]]))
        mv_rate = int(0.5 + (result[0][self.gender == 'female'] * max(final) / 12))
        return mv_rate                                      # returned value is rounddown(race * class / 12)

    def assign_name(self, str_input):
        self.character_name = str_input


# some_dude = Character(level=5, race="Halfling", classes=['Fighter', 'Thief'],
#                       attrib_list=[{'Str': 14, 'Int': 13, 'Wis': 9, 'Dex': 15, 'Con': 18, 'Cha': 11, 'Com': 4},
#                                    {'Str': 0, 'Int': 0, 'Wis': 0, 'Dex': 0, 'Con': 0, 'Cha': 0, 'Com': 0}])
# print(some_dude.__dict__)


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
