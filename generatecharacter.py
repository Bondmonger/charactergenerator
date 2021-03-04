import random
import csv
import attributes


def roll(a):  # rolls a single die of "a" sides
    return random.randrange(1, a + 1)


def display_classes(ch_classes):  # sorts classes and converts list to a slash-separated string
    displayed_class = ""
    ch_classes.sort()
    for a in range(len(ch_classes)):
        displayed_class = displayed_class + ch_classes[a] + '/'
    displayed_class = displayed_class.rstrip('/')
    return displayed_class


def display_level(levels):  # converts the list of levels into a displayable string
    displayed_level = ""
    for a in range(len(levels)):
        displayed_level = displayed_level + str(levels[a]) + '/'
    displayed_level = displayed_level.rstrip('/')
    return displayed_level


# TO DO LIST

# 1) still need a mechanism to prevent 0-hp leveling events with negative constitution
#       except do we though? I kinda like this mechanic the way it is
#       also Barbarian max wis isn't coded in anywhere (unnecessary?)
# 2) standardize output for methods I through V
#       add some toggle-able randomizer code for methods I through V (for bulk testing without user entry)
# 	    break selectclass.eligibility and selectclass.eligible_races into smaller functions to reduce redundancy
# 	    do we need an eligible_classes counterpart to eligible_races / can it be made reversible?
# 	    switch race/class selection routines into tkinter with buttons
#       strict 'level-5-fighter' gen
##################################################################
# INTERFACE
#   create level/race/class selection fields for method VI (including random options for all three)
#   fold in the other character attribute methods (I through V)
#       dovetail those into the character class (or maybe create a separate class definition for each method?)
#   OUTSTANDING: alignment, equipment, proficiencies, spells, race/class abilities, languages
##################################################################
# 4) figure out storage/equipment fields
#       csv all the armor and weapons
#       weapon proficiencies
#       multi-attack
# 5) dual-classing and bards
# 6) stat up 0-level humans, demi-humans & wights
# 7) add in special abilities/special ability fields
#       spells per level
#       thief-like abilities
#       psionics
#       miscellaneous ability/resistance definitions


def clip_surplus_dict(race, attrs, excess):  # nips the tops off attributes above racial maximum
    ord_attrs, rac_max = ['Str', 'Int', 'Wis', 'Dex', 'Con', 'Cha', 'Com'], attributes.racial_maximums(race)
    temp_excess = dict(zip(ord_attrs, rac_max))
    temp_excess['Wis'] = 25
    for k, v in temp_excess.items():
        temp_excess[k] = attrs[k] - temp_excess[k]
        if temp_excess[k] < 0:
            temp_excess[k] = 0
        attrs[k] -= temp_excess[k]  # trims attributes
        excess[k] += temp_excess[k]  # updates excess
    return


def primary_att(cha_class):                     # returns minimum attributes for the 10% xp bonus
    maxxp, xps, final, attnames = open('xpvalues.csv'), [], [], ["str", "int", "wis", "dex", "con", "cha", "com"]
    for row in csv.reader(maxxp):               # calls the relevant xp row from xpvalues.csv
        if cha_class == row[0]:
            xps = row[0:28]
    for a in range(7):
        m = xps[1].find(attnames[a])            # searches for attribute name in primary att field ("str16", etc)
        if m == -1:
            final.append(m)                     # if not found, sets min to -1 (to be replaced with racial minimum)
        else:
            final.append(int(xps[1][m+3:m+5]))  # if found, sets min equal to the next two character (16 or whatever)
    if sum(final) == -7:
        final = []
        for a in range(7):
            final.append(26)                    # if no primary attribute then minimums are all set at 26
    return final


def bonus_check(cha_class, atts):  # checks eligibility for 10% xp boost
    minimums = primary_att(cha_class)
    for attribute_score in range(7):
        if atts[attribute_score] < minimums[attribute_score]:
            return False
    return True


def return_xp(ch_class):  # returns the complete list of xp thresholds for the input character class
    xpindex, xpvalues = open('xpvalues.csv'), []
    for row in csv.reader(xpindex):
        if ch_class == row[0]:
            xpvalues.append(row)
            return xpvalues[0][2:28]  # ['0', '1500', '3000', ...]


def next_xp(classes, levels, attrs, diff=0):                                            # returns impending thresholds
    xpvalues, number_of_classes, attrs_list = [], len(classes), list(attrs.values())
    for a in range(number_of_classes):                                                  # diff = -1 is most recent
        subsequent_threshold = int(return_xp(classes[a])[levels[a] + diff])             # diff = 0 is imminent threshold
        xpvalues.append(subsequent_threshold * number_of_classes)                       # diff = 1 is 2 levels up, etc
        if bonus_check(classes[a], attrs_list) is True:
            xpvalues[a] = xpvalues[a] * 10 / 11
    return xpvalues                                                                     # [7272.7, 12000]


# test_class = ['Fighter', 'Cleric']
# test_level = [2, 3]
# test_attrs = {'Str': 17,'Int': 7, 'Wis': 13, 'Dex': 10, 'Con': 14, 'Cha': 9, 'Com': 6}
# print(next_xp(test_class, test_level, test_attrs, -1))


def increment_xp(classes, levels, xp, atts):                    # increments levels until all xp are spent
    temp = next_xp(classes, levels, atts)
    nextlevel, nextxp_class = temp[temp.index(min(temp))], []
    while nextlevel <= xp:
        levels[temp.index(min(temp))] += 1
        temp = next_xp(classes, levels, atts)
        nextlevel = temp[temp.index(min(temp))]                 # Modifies levels[]
    nextxp_class.append(nextlevel)
    nextxp_class.append(classes[temp.index(min(temp))])
    return nextxp_class                                         # ...and returns the impending level threshold


def flatten(x):                                                 # adds up the elements in nested HP list(s)
    temp = []
    for a in range(len(x)):
        for b in range(len(x[a])):
            temp.append(x[a][b])
    return round(sum(temp)/(len(x)-1))


def generate_level(attrs, ch_classes, race, xp, excess):        # creates and updates levels and xp thresholds
    levels, final = [], {}
    for a in range(len(ch_classes)):
        levels.append(0)
    clip_surplus_dict(race, attrs, excess)
    if ch_classes[0] == "0-level":
        final['next_level'] = ["not applicable", "0-level"]
    else:
        next_level = increment_xp(ch_classes, levels, xp, attrs)
        final['next_level'] = next_level
        final['level'] = levels
    return final


def pc_xp(level):                                               # returns a randomized xp value for a given level
    base, increments, value = [], [], 0
    with open('xpvalues.csv') as currentxp:
        for row in csv.reader(currentxp):
            if "MeanSum" == row[0]:
                base.append(row)
            if "MeanDif" == row[0]:
                increments.append(row)
    base, increments = base[0][1:28], increments[0][2:28]       # note the differing start points
    value = int(base[level]) + roll(int(increments[level]))     # this is to turn increments[level + 1] to [level]
    return value


def impending_mean_xp(xp):                                      # returns the next mean xp threshold (an integer)
    base = []
    with open('xpvalues.csv') as currentxp:
        for row in csv.reader(currentxp):
            if "MeanSum" == row[0]:
                base.append(row)
    base = base[0][2:28]
    for a in base:
        if xp < int(a):
            return a


# not in use
# character_dict = {'Race': [], 'Class': [], 'hp': [], 'Str': [], 'Int': [], 'Wis': [], 'Dex': [], 'Con': [], 'Cha': [],
#                   'Com': []}


# def make_character(gender, race, xp, ch_classes):
#     bundled_atts = attributes.methodvi(race, ch_classes)
#     final = generate_level(bundled_atts, ch_classes, race, xp)
#     final['hp'] = hitpoints.generate_hp(final['classes'], final['levels'], final['attributes'][4])
#     final['size'] = heightweight.size(race, gender)
#     display_attributes(final)
#     character_dict['Race'].append(final['race'])
#     character_dict['Class'].append(final['display_classes'])
#     character_dict['hp'].append([flatten(final['hp'])])
#     character_dict['Str'].append(final['attributes'][0])
#     character_dict['Int'].append(final['attributes'][1])
#     character_dict['Wis'].append(final['attributes'][2])
#     character_dict['Dex'].append(final['attributes'][3])
#     character_dict['Con'].append(final['attributes'][4])
#     character_dict['Cha'].append(final['attributes'][5])
#     character_dict['Com'].append(final['attributes'][6])
#     return final


# make_character("male", "Mountain Dwarf", pc_xp(4), ["Fighter", "Cleric"])


# for individuals in range(10):
#     race = selectclass.random_race()
#     make_character("male", race, pc_xp(3), selectclass.random_class(race))


# print("Str: "+str(round(sum(character_dict['Str'])/len(character_dict['Str']), 2)))
# print("Int: "+str(round(sum(character_dict['Int'])/len(character_dict['Int']), 2)))
# print("Wis: "+str(round(sum(character_dict['Wis'])/len(character_dict['Wis']), 2)))
# print("Dex: "+str(round(sum(character_dict['Dex'])/len(character_dict['Dex']), 2)))
# print("Con: "+str(round(sum(character_dict['Con'])/len(character_dict['Con']), 2)))
# print("Cha: "+str(round(sum(character_dict['Cha'])/len(character_dict['Cha']), 2)))
# print("Com: "+str(round(sum(character_dict['Com'])/len(character_dict['Com']), 2)))
