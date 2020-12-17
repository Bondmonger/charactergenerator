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
    def __init__(self, level):
        self.gender = selectclass.random_gender()
        self.race = selectclass.random_race()
        self.classes = selectclass.random_class(self.race)
        self.xp = generatecharacter.pc_xp(level)
        self.attributes = attributes.methodvi(self.race, self.classes)
        self.excess, self.attributes = self.attributes.pop(1), self.attributes[0]
        self.age = agevalues.generate_age(self.race, self.classes, level)
        for k, v in self.attributes.items():
            self.attributes[k] = self.attributes[k] + self.age[3][k]
        self.display_class = generatecharacter.display_classes(self.classes)
        self.level = generatecharacter.generate_level(self.attributes, self.classes, self.race, self.xp, self.excess)
        self.level, self.next_level = self.level['level'], self.level.pop('next_level')
        self.hp_history = hitpoints.generate_hp(self.classes, self.level, self.attributes['Con'])
        self.size = heightweight.size(self.race, self.gender)
        self.hp = generatecharacter.flatten(self.hp_history)
        return

    def display_attributes(self):  # displays attributes in the terminal
        archetypes = []
        for obj in range(len(self.classes)):
            archetypes.append(attributes.archetype(self.classes[obj]))
        if self.attributes['Str'] == 18 and self.attributes['Exc'] > 0 and "Fighter" in archetypes:
            displaystr = str(self.attributes['Str']) + '/' + str(self.attributes['Exc']).zfill(2)
        else:
            displaystr = str(self.attributes['Str'])
        print("{} {} {} {} --- hp: {} | hgt: {}'{}” wgt: {} lbs  age: {} ({}) --- str: {}, int {}, wis {}, dex {}, con "
            "{}, cha {}".format(generatecharacter.display_level(self.level), self.gender, self.race, self.display_class,
            str(self.hp), str(self.size[0] / 12)[0:1], str(self.size[0] % 12), str(self.size[1]), str(self.age[0]),
            self.age[1], displaystr, str(self.attributes['Int']), str(self.attributes['Wis']),
            str(self.attributes['Dex']), str(self.attributes['Con']), str(self.attributes['Cha'])))
        return

    def modify_str(self, adjustment):
        max_strength = attributes.racial_maximums(self.race)[0]  # used at the end
        self.attributes['Str'] += adjustment
        if self.attributes['Str'] > 17:
            max_racial_str = attributes.exceptional_str(self.race)
            while self.attributes['Str'] > 18:  # converts strength values above 18 into excess points
                self.attributes['Str'] -= 1
                self.excess['Str'] += 1
            self.attributes['Exc'] += self.excess['Str'] * 10  # dumps excess points into exceptional strength (*10)
            self.excess['Str'] = 0  # tares excess to zero
            if self.attributes['Exc'] > max_racial_str:
                while self.attributes['Exc'] > max_racial_str + 9:
                    self.excess['Str'] += 1
                    self.attributes['Exc'] -= 10
                self.attributes['Exc'] = max_racial_str  # reduces exceptional strength to racial max (if necessary)
            if self.attributes['Exc'] > 100:
                while self.attributes['Exc'] > 100:
                    self.attributes['Str'] += 1
                    self.attributes['Exc'] -= 10
                self.attributes['Exc'] = 100  # converts +00 percentile scores into 19+ strength
        if self.attributes['Str'] > max_strength:  # for low maximum strength races (halfling, drow, etc)
            self.excess['Str'] += self.attributes['Str'] - max_strength
            self.attributes['Str'] = max_strength
        return

    def modify_con(self, adjustment):
        max_constitution = attributes.racial_maximums(self.race)[4]
        self.attributes['Con'] += self.excess['Con'] + adjustment
        self.excess['Con'] = 0  # tares excess to zero
        if self.attributes['Con'] > max_constitution:
            self.excess['Con'] += self.attributes['Con'] - max_constitution
            self.attributes['Con'] = max_constitution
        con_posit = len(self.classes)
        self.hp_history[con_posit] = hitpoints.generate_hp(self.classes, self.level, self.attributes['Con'])[con_posit]
        self.hp = generatecharacter.flatten(self.hp_history)
        return

    def modify_other_att(self, adjustment, attribute):
        max_constitution = attributes.racial_maximums(self.race)[4]
        self.attributes[attribute] += self.excess[attribute] + adjustment
        self.excess[attribute] = 0  # tares excess to zero
        if self.attributes[attribute] > max_constitution:
            self.excess[attribute] += self.attributes[attribute] - max_constitution
            self.attributes[attribute] = max_constitution
        return

    def modify_attribute(self, attr, adjustment):
        if self.excess[attr] > 0 > adjustment:
            while adjustment < 0:
                self.excess[attr] -= 1
                adjustment += 1
            if adjustment == 0:
                return
        if attr == 'Str':
            self.modify_str(adjustment)
        if attr == 'Con':
            self.modify_con(adjustment)
            return
        if attr in ['Int', 'Wis', 'Dex', 'Cha', 'Com']:
            self.modify_other_att(adjustment, attr)
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
        self.xp += adjustment
        return

    def calculate_level(self, adj=0):                           # also updates hit points
        if max(self.level) + adj < 1:                           # 1st level energy drain targets become wights
            print("This is a wight")
            return
        current_xp_floor = max(generatecharacter.next_xp(self.classes, self.level, self.attributes, -1))
        current_xp_ceiling = min(generatecharacter.next_xp(self.classes, self.level, self.attributes))
        if adj < 0:                                             # if the adjustment is negative...
            upper_thr = max(generatecharacter.next_xp(self.classes, self.level, self.attributes, adj))
            ind_pos = generatecharacter.next_xp(self.classes, self.level, self.attributes, adj).index(upper_thr)
            lower_threshold = generatecharacter.next_xp(self.classes, self.level, self.attributes, adj - 1)[ind_pos]
            self.xp = (lower_threshold + upper_thr) / 2         # ...sets xp to midpoint of destination level
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
        if self.xp >= current_xp_ceiling:                       # if xp are greater than the current ceiling...
            for ch_cl in range(number_of_classes):              # ...calculates additional hp
                hitpoints.hp_compute_mid(hp_calcs[ch_cl], self.hp_history[ch_cl], self.level[ch_cl],
                                         len(self.hp_history[ch_cl]))
                hitpoints.hp_compute_top(hp_calcs[ch_cl], self.hp_history[ch_cl], self.level[ch_cl])
        self.hp_history = self.hp_history[0:number_of_classes]  # recalculates con bonus from scratch
        hitpoints.con_bonus(self.hp_history, hp_calcs, self.attributes['Con'])
        if "Ninja" in self.classes:                             # ninjas require a special exception for con bonus
            for b in range(number_of_classes):
                self.hp_history[number_of_classes][b] *= 2
        self.hp = generatecharacter.flatten(self.hp_history)
        return


ident = {}

for a in range(10):
    temp = 'p' + str(a+1).zfill(2)
    ident[temp] = temp
    ident[temp] = Character(4)
    ident[temp].display_attributes()
    # ident[temp].modify_xp(1000)
    # ident[temp].calculate_level(0)
    # ident[temp].display_attributes()
    # print(ident[temp].__dict__)

# print('p01')
# print(list(ident.keys()))
# print(ident['p01'].hp)

    # ident[a].modify_age(1)
    # print(ident[a].__dict__)
    # ident[a].modify_attribute('Cha', +4)
    # print(ident[a].excess["Str"])

# print(ident[2].__dict__)
# print(p2.__dict__)
