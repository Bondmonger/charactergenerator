from functools import lru_cache
import csv


@lru_cache(maxsize=10)
def age_adj(age_categ):                                         # accepts age category ('young adult')
    temp = []                                                   # returns modifier ([0, 0, -1, 0, 1, 0, 0])
    with open('agecategories.csv') as bonuses:
        for row in csv.reader(bonuses):
            if age_categ == row[0]:
                for a in range(7):
                    temp.append(int(row[a + 1]))
    return temp


@lru_cache(maxsize=5000)                                        # THIS IS A SHITTY ONE
def age_cat(race, age):                                         # accepts ('High Elf', 452)    STR / INT
    temp, datacolumn, next_cat, firstrow = [], 10, 0, "Header"  # returns (['mature', 550])    STR / STR
    with open('attrbonuses.csv') as age_categories:
        for row in csv.reader(age_categories):
            if race == row[0]:
                while age > int(row[datacolumn]):
                    datacolumn += 1
                next_cat = row[datacolumn]
        age_categories.seek(0)                                  # resets counter
        for row in csv.reader(age_categories):
            if firstrow == row[0]:
                temp.append(row[datacolumn])
    temp.append(next_cat)                                       # type STR since it's used as a match value
    return temp


@lru_cache(maxsize=100)
def age_thresholds(race):                                       # accepts ('High Elf')
    thresholds = []                                             # returns ([99, 175, 550, 875, 1200, 1600])
    with open('attrbonuses.csv') as age_categories:
        for row in csv.reader(age_categories):
            if race == row[0]:
                for a in range(6):
                    thresholds.append(int(row[10+a]))
    return thresholds


@lru_cache(maxsize=100)
def racialsum(race):                                            # accepts ('High Elf')
    modifiersum = 0                                             # returns (2)
    with open('attrbonuses.csv') as racial_bonuses:             # ie, high elf atts are +2 (net) vs a human's
        for row in csv.reader(racial_bonuses):
            if race == row[0]:
                for a in range(1, 8):
                    modifiersum += int(row[a])
    return modifiersum


@lru_cache(maxsize=100)
def exceptional_str(race):                                      # accepts ('High Elf')
    with open('attrbonuses.csv') as bonuses:                    # returns (75)
        for row in csv.reader(bonuses):                         # ie, racial max on exc. strength
            if race == row[0]:
                maximum_exceptional_strength = int(row[8])
    return maximum_exceptional_strength


@lru_cache(maxsize=100)
def racial_attribute_bonus(race):                               # accepts ('High Elf')
    bonuses = []                                                # returns ([0, 0, 0, 1, -1, 0, 2])
    with open('attrbonuses.csv') as values:
        for row in csv.reader(values):
            if race == row[0]:
                for a in range(7):
                    bonuses.append(int(row[a+1]))
    return bonuses


@lru_cache(maxsize=100)
def racial_maximums(race):                                      # accepts ('High Elf')
    final = []                                                  # returns ([18, 18, 18, 19, 18, 18, 25])
    with open('attributemax.csv') as maxs:
        for row in csv.reader(maxs):
            if row[0] == race:
                for a in range(1, 8):
                    final.append(int(row[a]))
    return final


@lru_cache(maxsize=100)
def archetype(ch_class):                                        # accepts ('Ranger')
    with open('xpvalues.csv') as archetypes:                    # returns ('Fighter')
        for row in csv.reader(archetypes):
            if ch_class == row[0]:
                class_archetype = row[38]
    return class_archetype


@lru_cache(maxsize=400)
def age_variables(race, ch_class):          # returns a three-item list [base_age, #ofrolls, #ofsides]
    age_values, iterator, iterator_options = [], 0, ['Human', 'Fighter', 'Magic User', 'Cleric', 'Thief']
    archetype(ch_class)
    if race == 'Human':                     # humans get a unique age range for each subclass...
        race = ch_class
    else:                                   # ...while demi-human age is dictated by class archetype
        ch_class = archetype(ch_class)
        for i, option in enumerate(iterator_options):
            if ch_class == option:
                iterator = int(i) * 3       # the transpose-interval for the archetype's csv call (Thief is +12, etc)
    with open('attributemins.csv') as minput:
        for row in csv.reader(minput):
            if race == row[0]:
                for a in range(3):
                    attr_pos = 10 + iterator + a
                    age_values.append(int(row[attr_pos]))
    return age_values


@lru_cache(maxsize=400)
def minimum_sum(ch_class):                                      # accepts ('Ranger')
    classminimums, tempsum = open('attributemins.csv'), 0       # returns (67)
    for row in csv.reader(classminimums):
        if ch_class == row[0]:
            for a in range(1, 9):
                tempsum += int(row[a])
    return tempsum


@lru_cache(maxsize=100)
def minimums(cla_rac):                                          # accepts ('High Elf')
    final = []                                                  # returns ([3, 8, 3, 7, 6, 8, 3])
    with open('attributemins.csv') as mins:                     # handles both race and class arguments
        for row in csv.reader(mins):
            if cla_rac == row[0]:
                for a in range(1, 8):
                    final.append(int(row[a]))
    return final


@lru_cache(maxsize=100)                                 # calculates AC bonuses for non-armored characters
def class_ac(ch_classes, levels):                       # accepts (('Kensai'), (5))
    result, final = [], []                              # returns a Ternary transposer...
    for index, (ch_class, level) in enumerate(zip(ch_classes, levels)):
        with open('attributemins.csv') as ac_trans:
            for row in csv.reader(ac_trans):            # ...2 = Monk, 1 = Kensai, 0 = all other classes...
                if ch_class == row[0]:
                    result.append(int(row[76]))
        with open('levelvalues.csv') as ac_classmods:   # ...as well as a level modifier (based on transposed column)
            for row_lvl in csv.reader(ac_classmods):
                if level == int(row_lvl[0]):            # checks class against level to return an AC bonus
                    final.append(int(row_lvl[1+result[index]]))
        return max(final)


@lru_cache(maxsize=100)
def dex_acmultiplier(ch_classes):                       # accepts (('Monk'))
    result, final = [], 1                               # returns (0)
    with open('xpvalues.csv') as character_classes:     # the call filters non-Monks/non-Kensai
        for row in csv.reader(character_classes):
            for a, ch_class in enumerate(ch_classes):
                if ch_class == row[0]:
                    result.append(int(row[48]))
    for multiplier in result:                           # calculates a product of the dex multipliers
        final = final * multiplier                      # monks are 0x, barbarians are 2x, all others are 1x
    return final


@lru_cache(maxsize=25)
def dex_acbonus(dexterity):                             # accepts 17
    dex_ac = 0                                          # returns 3
    with open('attributevalues.csv') as dexbonus:
        for row in csv.reader(dexbonus):
            if str(dexterity) == row[0]:
                dex_ac = int(row[22])
    return dex_ac


@lru_cache(maxsize=400)                                 # calculates base movement for non-armored units
def race_class_movement(race, ch_classes):              # accepts ('Drow', tuple(['Fighter'])
    result = [[], []]                                   # returns [[12, 15], 0]
    with open('attributemins.csv') as movement_rates:
        for row in csv.reader(movement_rates):
            if race == row[0]:
                for male_female in range(2):            # populates racial movement [12, 12], for [male, female]
                    result[0].append(int(row[77+male_female]))
            for ch_class in ch_classes:
                if ch_class == row[0]:                  # populates class transposer mods (1 for monk, 2 for barb)
                    result[1].append(int(row[79]))
    return result                                       # result is male/female base values with class transposer


@lru_cache(maxsize=100)
def class_level_movement(levels, elig):                 # calculates movement for non-armored characters
    final = []                                          # elig is a ternary transposer (0="none", 1=Monk, 2=Barb)
    for index, (transposer, level) in enumerate(zip(elig, levels)):
        with open('levelvalues.csv') as move_mods:
            for row_lvl in csv.reader(move_mods):
                if level == int(row_lvl[0]):            # compares against class level to calculate movement
                    final.append(int(row_lvl[10+transposer]))
    return max(final)


@lru_cache(maxsize=25)
def comeliness_bonus(charisma):                         # applies charisma bonus to comeliness
    final = 0                                           # accepts 16
    with open('attributevalues.csv') as bonuses:        # returns 2
        for row in csv.reader(bonuses):
            if row[0] == str(charisma):
                final = int(row[41])
    return final


@lru_cache(maxsize=1000)
def base_thaco(classes, levels):                        # accepts (tuple['Assassin', 'Fighter'], tuple([4, 4])
    final = []                                          # returns 2
    for ch_class, level in zip(classes, levels):
        with open('xpvalues.csv') as th_trans:          # first we request a 'transposition' value by archetype
            for row in csv.reader(th_trans):
                if ch_class == row[0]:                  # 0 for F, 1 for C, 2 for T, 3 for M
                    result = int(row[51])
        with open('levelvalues.csv') as thaco_mod:
            for row_lvl in csv.reader(thaco_mod):
                if level == int(row_lvl[0]):            # then we use level/archetype to generate a base thac0 bonus...
                    final.append(int(row_lvl[5+result]))
    return max(final)                                   # ...and return the 'largest' of those


@lru_cache(maxsize=150)
def str_thacobonus(strength, exceptional, str_disp, multiplier):
    str_th = 0                                          # accepts (18, '18/20', 20, 1)
    if len(str_disp) > 2:
        with open('excstr.csv') as excbonus:            # checks for exceptional str
            for row in csv.reader(excbonus):
                if exceptional > int(row[0]):
                    str_th = int(row[1]) * multiplier
    else:                                               # ...then calculates for non-exceptional str
        with open('attributevalues.csv') as strbonus:
            for line in csv.reader(strbonus):
                if strength == int(line[0]):
                    str_th = int(line[1]) * multiplier
    return str_th                                       # returns thaco modifier from strength


@lru_cache(maxsize=150)
def str_damagebonus(strength, exceptional, str_disp, multiplier):
    str_dmg = 0                                         # accepts (18, '18/20', 20, 1)
    if len(str_disp) > 2:                               # returns 3
        with open('excstr.csv') as excbonus:
            for row in csv.reader(excbonus):
                if exceptional > int(row[0]):
                    str_dmg = (row[2]) * multiplier
    else:                                               # ...then calculates for non-exceptional str
        with open('attributevalues.csv') as strbonus:
            for line in csv.reader(strbonus):
                if strength == int(line[0]):
                    str_dmg = int(line[2]) * multiplier
    return str_dmg                                      # returns damage modifier from strength


@lru_cache(maxsize=150)
def str_multiplier(classes):                            # accepts (tuple['Fighter'])
    result, final = [], 1                               # returns 1
    with open('xpvalues.csv') as character_classes:
        for row in csv.reader(character_classes):
            for ch_class in classes:
                if ch_class == row[0]:
                    result.append(int(row[49]))
    for a in result:                                    # calculates the product of str multipliers
        final = final * a                               # monks are 0x, all others are 1x
    return final


@lru_cache(maxsize=100)
def call_hp(ch_class):                                  # accepts 'Fighter'
    result = []                                         # returns [7, 1, 3, 10, 9, 3, 7, 1, 0]
    with open('xpvalues.csv') as character_classes:
        for row in csv.reader(character_classes):
            if ch_class == row[0]:
                for a in range(9):
                    result.append(int(row[39+a]))
    return result  # [1HD, 1#rolls, 1bon, midLevelHD, midCap, maxIncrs, max_con_bonus, bonus_multiplier, fixed_bonus]


@lru_cache(maxsize=25)
def con_hpbonus(constitution):                          # accepts 17
    with open('attributevalues.csv') as attr_bonuses:   # returns 3
        for row in csv.reader(attr_bonuses):
            if str(constitution) == row[0]:
                bonus = int(row[29])
    return bonus


@lru_cache(maxsize=50)
def demote_class(cha_class):                            # accepts 'Fighter'
    with open('xpvalues.csv') as characterclasses:      # returns '0-level'
        for row in csv.reader(characterclasses):
            if cha_class == row[0]:
                result = row[37]
    return result


@lru_cache(maxsize=50)
def ua_attr(ch_class):                                  # accepts 'Fighter'
    v_values = []                                       # returns [9, 3, 5, 7, 8, 6, 4]
    with open('xpvalues.csv') as ua_dice:
        for row in csv.reader(ua_dice):
            if ch_class == row[0]:
                for a in range(7):
                    v_values.append(int(row[a + 29]))
    return v_values


@lru_cache(maxsize=100)
def return_xp(ch_class):
    base = []
    with open('xpvalues.csv') as currentxp:
        for row in csv.reader(currentxp):
            if ch_class == row[0]:
                base.append(row)
    return base


@lru_cache(maxsize=100)
def xp_bonus_check(cha_class):                  # accepts 'Fighter'
    xps, final = [], []                         # returns [16, -1, -1, -1, -1, -1, -1]
    with open('xpvalues.csv') as maxxp:
        for row in csv.reader(maxxp):           # calls the relevant xp row from xpvalues.csv
            if cha_class == row[0]:
                xps = row[0:28]
    for value in ["str", "int", "wis", "dex", "con", "cha", "com"]:
        m = xps[1].find(value)                  # searches for attribute name in primary att field ("str16", etc)
        if m == -1:
            final.append(m)                     # if not found, sets min to -1 (to be replaced with racial minimum)
        else:
            final.append(int(xps[1][m+3:m+5]))  # if found, sets min equal to the next two character (16,etc)
    if sum(final) == -7:
        final = []
        for a in range(7):
            final.append(26)                    # if no primary attribute then minimums are all set at 26
    return final


@lru_cache(maxsize=100)
def call_height_weight(race):
    result = []
    with open('attrbonuses.csv') as sizevalues:
        for row in csv.reader(sizevalues):
            if race == row[0]:  # populates result list with height/weight values for the provided race
                for a in range(26):
                    result.append(int(row[a + 18]))
    return result
