import random
import csv
import attributes
import hitpoints
import agevalues
import heightweight
import selectclass


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


# hpexample = generate_hp(["Fighter", "Magic User", "Thief"], [3,3,3])
# print str(hpexample) + "/3"
# print int(sum(hpexample)/3.0 + 0.5)

# BUG extermination:
# a) age modifiers were not affecting STR and INT
# b) height/weight randomizer was failing once in 600 (needed to change >= to >)

# TO DO LIST

# 1) still need a mechanism to prevent 0-hp leveling events with negative constitution
#       except do we though? I kinda like this mechanic the way it is
#       also Barbarian max wis isn't coded in anywhere (unnecessary?)
#       need to add age increments for character creation leveling events (is this a separate task?)
# 2) add methods I through V to attributes.py
#       still need to standardize outputs (methodvi currently returns [12, 7, 9, 11, 10, 8, 6 [0, 0, 0, 0, 0, 0, 0]])
#           to make methods I-V work we need to modify the driver code in make_character send/receive race/class
#           also need to add in racial bonuses before the attributes are passed back to generatecharacter.py
##################################################################
##################################################################
#       need a modify_attribute function
#       need to create a racial max check (to run after the age determination)
#           points trimmed must be checked against the surplus list
#       need a modify_age function
#       need a modify_level function
#           this may as well be a modify_xp function
#           but here is where we get into the character as class issue
##################################################################
##################################################################
# 	    break selectclass.eligibility and selectclass.eligible_races into smaller functions to reduce redundancy
# 	    do we need an eligible_classes counterpart to eligible_races / can it be made reversible?
#       convert more of the attribute creation routines into zips - this is templated at attributes.methodv
# 	    switch those race/class selection routine into tkinter with buttons
#       add some toggle-able randomizer code for methods I through V (for bulk testing without user entry)
#       strict 'level-5-fighter' gen
# 4) create a function for incrementing levels with xp awards:
#       create a statement preventing multiple leveling events for a given class
#       calculate/update hit points
#       create a de-leveling function
#       ping age increases
#       stat up 0-level humans/demi-humans
# 5) dual-classing and bards
# 6) figure out storage/equipment fields
#       csv all the armor and weapons
# 7) add in special abilities/special ability fields
#       spells per level
#       thief-like abilities
#       weapon proficiencies
#       multi-attack
#       psionics
#       miscellaneous ability/resistance definitions

def return_xp(ch_class):  # returns xp thresholds for the input character class
    xpindex, xpvalues = open('xpvalues.csv'), []
    for row in csv.reader(xpindex):
        if ch_class == row[0]:
            xpvalues.append(row)
            return xpvalues[0][2:]


def primary_att(cha_class):  # returns minimum attributes for the 10% xp bonus
    maxXP, xps, final, attnames = open('xpvalues.csv'), [], [], ["str", "int", "wis", "dex", "con", "cha", "com"]
    for row in csv.reader(maxXP):  # calls the relevant xp row from xpvalues.csv
        if cha_class == row[0]:
            xps.append(row[0:28])
            xps = xps[0]
    for a in range(7):
        m = xps[1].find(attnames[a])  # searches for each attribute name in the primary att field ("str16", etc)
        if m == -1:
            final.append(m)  # if attribute isn't there, sets min to -1 (to be replaced with racial minimum)
        else:
            final.append(int(xps[1][m+3:m+5]))  # if attribute is there, sets min equal to the next two character (16)
    if sum(final) == -7:
        final = []
        for a in range(7):
            final.append(26)  # if the class has no primary attribute then the minimums are all set to 26
    return final


def bonus_check(cha_class, atts):  # checks eligibility for 10% xp boost
    minimums = primary_att(cha_class)
    for attribute_score in range(7):
        if atts[attribute_score] < minimums[attribute_score]:
            return False
    return True


def next_xp(classes, levels, atts):  # returns list of impending xp thresholds
    temp, xpvalues, att_bonus, number_of_classes = [], [], 0.0, len(classes)
    for a in range(number_of_classes):
        temp.append(return_xp(classes[a]))
        xpvalues.append(number_of_classes * int(temp[a][levels[a]]))
        if bonus_check(classes[a], atts) == 1:
            xpvalues[a] = xpvalues[a] * 10 / 11
    return xpvalues


def increment_xp(classes, levels, xp, atts):
    # increments levels until all xp are spent. Modifies levels[] and returns the subsequent level threshold
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


def flatten(x):  # adds up the elements in the nested HP list(s)
    temp = []
    for a in range(len(x)):
        for b in range(len(x[a])):
            temp.append(x[a][b])
    return round(sum(temp)/(len(x)-1))


def display_attributes(final):  # displays labels attributes in the terminal
    if final['attributes'][0] == 18 and final['attributes'][7] > 0:
        displaystr = str(final['attributes'][0])+'/'+str(final['attributes'][7]).zfill(2)
    else:
        displaystr = str(final['attributes'][0])
    print(str(display_level(final['levels']))+' '+str(final['race'])+' '+str(final['display_classes'])+' --- hp: ' +
          str(flatten(final['hp']))+' | hgt: '+str(final['size'][0]/12)[0:1]+"'"+str(final['size'][0] % 12)+'"  wgt: ' +
          str(final['size'][1])+' lbs  age: ' + str(final['age'][0])+' ('+final['age'][1]+') --- str: '+displaystr +
          ', int: '+str(final['attributes'][1]) + ', wis: '+str(final['attributes'][2]) + ', dex: '
          + str(final['attributes'][3])+', con: '+str(final['attributes'][4])+', cha: ' + str(final['attributes'][5]))
          # + ' --- '+str(final['next_level'][0])+', '+final['next_level'][1])


def generate_level(re_attached, ch_classes, race, xp):
    # updates re_attached[] to contain class(es), race, levels, xp and next-level values
    levels, atts_list, age_object = [], [], agevalues.generate_age(race, ch_classes)
    for a in range(len(ch_classes)):
        levels.append(0)
    classes = display_classes(ch_classes)
    final = {'attributes': re_attached[0], 'excess': re_attached[1], 'classes': ch_classes, 'display_classes': classes,
             'race': race, 'levels': levels, 'xp': xp, 'age': age_object}
    for a in range(7):
        final['attributes'][a] += final['age'][3][a]
    new_excess = attributes.clip_surplus(race, final['attributes'])
    for a in range(7):
        final['excess'][a] += new_excess[a]
    if ch_classes[0] == "0-level":
        final['next_level'] = ["not applicable", "0-level"]
    else:
        next_level = increment_xp(final['classes'], final['levels'], final['xp'], final['attributes'])
        final['next_level'] = next_level
    return final


character_dict = {'Race': [], 'Class': [], 'hp': [], 'Str': [], 'Int': [], 'Wis': [], 'Dex': [], 'Con': [], 'Cha': [],
                  'Com': []}


def make_character(gender, race, xp, ch_classes):
    bundled_atts = attributes.methodvi(race, ch_classes)
    final = generate_level(bundled_atts, ch_classes, race, xp)
    final['hp'] = hitpoints.generate_hp(final['classes'], final['levels'], final['attributes'][4])
    final['size'] = heightweight.size(race, gender)
    display_attributes(final)
    character_dict['Race'].append(final['race'])
    character_dict['Class'].append(final['display_classes'])
    character_dict['hp'].append([flatten(final['hp'])])
    character_dict['Str'].append(final['attributes'][0])
    character_dict['Int'].append(final['attributes'][1])
    character_dict['Wis'].append(final['attributes'][2])
    character_dict['Dex'].append(final['attributes'][3])
    character_dict['Con'].append(final['attributes'][4])
    character_dict['Cha'].append(final['attributes'][5])
    character_dict['Com'].append(final['attributes'][6])


def pc_xp(level):  # returns a randomized xp value for an NPC of level "level"
    currentXP, base, increments, value = open('xpvalues.csv'), [], [], 0
    for row in csv.reader(currentXP):
        if "MeanSum" == row[0]:
            base.append(row)
        if "MeanDif" == row[0]:
            increments.append(row)
    base, increments = base[0], increments[0]
    value = int(base[level + 1]) + roll(int(increments[level + 2]))
    return value


# make_character("male", "Mountain Dwarf", pc_xp(4), ["Fighter", "Cleric"])


for individuals in range(100):
    race = selectclass.random_race()
    make_character("male", race, pc_xp(3), selectclass.random_class(race))


# class Person:
#   def __init__(self, name, age):
#     self.name = name
#     self.age = age
#
# p1 = Person("John", 36)
# p2 = Person("Carol", 28)
#
# print(vars(p1))
# print(p2.__dict__)


print("Str: "+str(round(sum(character_dict['Str'])/len(character_dict['Str']), 2)))
print("Int: "+str(round(sum(character_dict['Int'])/len(character_dict['Int']), 2)))
print("Wis: "+str(round(sum(character_dict['Wis'])/len(character_dict['Wis']), 2)))
print("Dex: "+str(round(sum(character_dict['Dex'])/len(character_dict['Dex']), 2)))
print("Con: "+str(round(sum(character_dict['Con'])/len(character_dict['Con']), 2)))
print("Cha: "+str(round(sum(character_dict['Cha'])/len(character_dict['Cha']), 2)))
print("Com: "+str(round(sum(character_dict['Com'])/len(character_dict['Com']), 2)))

