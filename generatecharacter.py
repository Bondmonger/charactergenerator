import random
import csv
import attributes
import hitpoints
import agevalues
import heightweight

# from writetoexcel import writetosheet


def roll(a):
    # rolls a single die of "a" sides
    return random.randrange(1, a + 1)


def display_classes(ch_classes):
    # converts the list of classes into a string
    # coincidentally, this is also where the classes list gets sorted prior to incrementing the levels
    a, i, ch_class = len(ch_classes), 0, ""
    ch_classes.sort()    
    while i < a:
        ch_class = ch_class + ch_classes[i] + '/'
        i += 1
    ch_class = ch_class.rstrip('/')
    return ch_class


def display_level(levels):
    # converts the list of levels into a displayable string
    if len(levels) == 1:
        lvl = str(levels[0])
    elif len(levels) == 2:
        lvl = str(levels[0])+'/'+str(levels[1])
    else:
        lvl = str(levels[0])+'/'+str(levels[1])+'/'+str(levels[2])
    return lvl


# hpexample = generate_hp(["Fighter", "Magic User", "Thief"], [3,3,3])
# print str(hpexample) + "/3"
# print int(sum(hpexample)/3.0 + 0.5)

# We've got the xp/leveling system implemented below.  The next step
# is to modify these hp compute values to work with the leveler.  Few
# items on the to do list:
# 1) we still need a mechanism to prevent 0-hp leveling events with neg. con
#       Except do we though? I kinda like this mechanic the way it is
#       Also Barbarian max wis is not coded in (unnecessary?)
# 2) need to add age and leveling events (is this a separate task?)
#       might as well do height/weight at the same time
# 3) add methods I through V to attributes.py
# 4) create a character gen randomizer
#       big hurdle: the weighted selection system
#       xp-based party gen AND strict level-5-fighter gen
# 5) create a function for incrementing levels with xp awards:
#       create a statement preventing multiple leveling events for a given class
#       create a de-leveling function
#       stat up 0-level humans/demi-humans
# 6) dual-classing and bards
# 7) figure out storage/equipment fields
#       csv all the armor and weapons
# 8) add in special abilities/special ability fields
#       weapon proficiencies
#       multi-attack
#       thief-like abilities
#       spells per level
#       psionics
#       miscellaneous abilities/resistances definitions


def return_xp(ch_class):
    # returns xp thresholds for the input character class
    xpindex, xpvalues = open('xpvalues.csv'), []
    for row in csv.reader(xpindex):
        if ch_class == row[0]:
            xpvalues.append(row)
            return xpvalues[0][2:]


def primary_att(cha_class):
    # returns minimum attributes for the 10% xp bonus
    # FOR statement calls the relevant xp row from xpvalues.csv
    # WHILE returns ordered list of minimum values (-1 fillers)
    # IF statement returns a null value for 'no primary attribute'
    maxXP, xps, final, attnames, i = open('xpvalues.csv'), \
        [], [], ["str","int","wis","dex","con","cha","com"], 0
    for row in csv.reader(maxXP):
        if cha_class == row[0]:
            xps.append(row[0:28])
            xps = xps[0]
    while i < 7:
        m = xps[1].find(attnames[i])
        if m == -1:
            final.append(m)
        else:
            final.append(int(xps[1][m+3:m+5]))
        i += 1
    if sum(final) == -7:
        i, final = 0, []
        while i < 7:
            final.append(26)
            i += 1
    return final


def bonus_check(cha_class, atts):
    # returns 1 for xp bonus and 0 for no xp bonus
    minimums, i, bonus, nobonus = primary_att(cha_class), 0, 1, 0
    while i < 7:
        if atts[i] < minimums[i]:
            return nobonus
        else:
            i += 1
    return bonus


def next_xp(classes, levels, atts):
    # returns list of all upcoming xp thresholds
    temp, xpvalues, i, att_bonus = [], [], 0, 0.0
    while i < len(classes):
        temp.append(return_xp(classes[i]))
        xpvalues.append(len(classes) * int(temp[i][levels[i]]))
        if bonus_check(classes[i], atts) == 1:
            xpvalues[i] = xpvalues[i] * 10 / 11
        i += 1
    return xpvalues


def increment_xp(classes, levels, xp, atts):
    # increments levels until all xp have been spent. Modifies levels[]
    # and returns the subsequent level threshold
    temp = next_xp(classes, levels, atts)
    nextlevel, nextxp_class = temp[temp.index(min(temp))], []
    while nextlevel <= xp:
        levels[temp.index(min(temp))] += 1
        # print(nextlevel)
        # print(classes[temp.index(min(temp))] + ' has gone up a level!')
        temp = next_xp(classes, levels, atts)
        nextlevel = temp[temp.index(min(temp))]
    nextxp_class.append(nextlevel)
    nextxp_class.append(classes[temp.index(min(temp))])
    return nextxp_class


def flatten(x):
    # quick-and-dirty hp calculator
    i, j, temp = 0, 0, []
    while i < len(x):
        while j < len(x[i]):
            temp.append(x[i][j])
            j += 1
        i += 1
        j = 0
    return round(sum(temp)/(len(x)-1))


def generate_level(re_attached, ch_classes, race, xp):
    # updates re_attached[] to contain class(es), race, levels,
    # xp and next-level values
    i, j, levels, atts_list, age_object = 0, 0, [], [], agevalues.generate_age(race, ch_classes)
    while i < len(ch_classes):
        levels.append(0)
        i += 1
    classes = display_classes(ch_classes)
    final = {'attributes': re_attached[0], 'excess': re_attached[1]}
    final['classes'] = ch_classes
    final['display_classes'] = classes
    final['race'] = race
    final['levels'] = levels
    final['xp'] = xp
    final['age'] = age_object
    while i < 7:
        final['attributes'][i] += final['age'][3][i]
        i += 1
    if ch_classes[0] == "0-level":
        final['next_level'] = ["not applicable", "0-level"]
    else:
        next_level = increment_xp(final['classes'], final['levels'], final['xp'], final['attributes'])
        final['next_level'] = next_level
    return final


def make_character(gender, race, xp, pcnum, *ch_classes):
    ch_classes, i = list(ch_classes), 0
    bundled_atts = attributes.methodVI(race, ch_classes)
    final = generate_level(bundled_atts, ch_classes, race, xp)
    final['hp'] = hitpoints.generate_hp(final['classes'], final['levels'], final['attributes'][4])
    final['size'] = heightweight.size(race, gender)
    print(str(display_level(final['levels']))+' '+str(final['race'])+' '+str(final['display_classes'])+' --- hp: '+str(flatten(final['hp']))+
          ' | age: '+str(final['age'][0])+'('+final['age'][1]+') --- str: '+str(final['attributes'][0])+', int: '+str(final['attributes'][1])+
          ', wis: '+str(final['attributes'][2])+', dex: '+str(final['attributes'][3])+', con: '+str(final['attributes'][4])+', cha: '+
          str(final['attributes'][5])+' --- '+str(final['next_level'][0])+', '+final['next_level'][1])
    print(final)
    # writetosheet(final, pcnum)


chars = 2
while chars < 12:
    make_character("male", "Gnome", 55000, chars, 'Fighter', 'Illusionist')
    chars +=1


# not in use
def npc_xp(level):
    # returns a randomized xp value for an NPC of level "level"
    currentXP, base, increments, value = open('xpvalues.csv'), [], [], 0
    for row in csv.reader(currentXP):
        if "MeanSum" == row[0]:
            base.append(row)
        if "MeanDif" == row[0]:
            increments.append(row)
    base, increments = base[0], increments[0]
    value = int(base[level + 1]) + roll(int(increments[level + 2]))
    return value


# not in use
def display_attributes(atts):
    # displays attributes
    print(atts[-9] + ' ' + atts[-8] + '\nHP: ' + str(atts[-10]) + '"' + "\nAC: " + str(atts[-11]) + '"')
    print("Str: " + str(atts[-7]) + "\nInt: " + str(atts[-6]) + \
    "\nWis: " + str(atts[-5]) + "\nDex: " + str(atts[-4]) + \
    "\nCon: " + str(atts[-3]) + "\nCha: " + str(atts[-2]) + \
    "\nCom: " + str(atts[-1]) + "\n")


# not in use
def armor(armor):
    # converts armor STRs into INT values
    ac, ad = 10, armor[-12]
    if ad == "none":
        ac = 10
    elif ad == "leather armor" or ad == "padded armor":
        ac = 8
    elif ad == "studded leather" or ad == "ring mail":
        ac = 7
    elif ad == "scale mail":
        ac = 6
    elif ad == "chain mail" or ad == "elfin chain":
        ac = 5
    elif ad == "splint mail" or ad == "banded mail":
        ac = 4
    elif ad == "plate mail":
        ac = 3
    elif ad == "field plate":
        ac = 2
    elif ad == "full plate":
        ac = 1
    return ac
