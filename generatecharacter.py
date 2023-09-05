import random
import datalocus


def roll(a):  # rolls a single die of "a" sides
    return random.randrange(1, a + 1)


def display_classes(ch_classes):  # sorts classes and converts list to a slash-separated string
    displayed_class = ""
    ch_classes.sort()
    for ch_class in ch_classes:
        displayed_class = displayed_class + ch_class + '/'
    displayed_class = displayed_class.rstrip('/')
    return displayed_class


def display_level(levels):  # converts the list of levels into a displayable string
    displayed_level = ""
    for level in levels:
        displayed_level = displayed_level + str(level) + '/'
    displayed_level = displayed_level.rstrip('/')
    return displayed_level


# regarding attributes.py, here are some improvements we could make down the road
#   a) switch the csv calls to serialized calls (pickle or json)
#   b) we could flatten out a lot of these nested conditionals via zip re-ordering
#   c) upgrade the RNG
#   d) a longitudinal analysis tool (hit points per level per class, for instance)
#
# 1) need a mechanism to prevent 0-hp leveling events with negative constitution, except do we though? I kinda like it
#       Barbarian max wis isn't coded in anywhere (unnecessary?)
# 2) strict by-level character generation
# 3) INTERFACE
#   COMPLETE [attribute methods III, IV & V]
#   COMPLETE [universal path to main menu]
#   COMPLETE [path to method screen from character sheet]
#   COMPLETE [character sheet ADD button made context sensitive]
#   COMPLETE [all-purpose re-roll button]
#   COMPLETE [add racial bonus info to the header]
#   COMPLETE [collapse frame/label names in header routines]
#   COMPLETE [need level/gender dropdowns for all methods]
#   COMPLETE [bug: name-level hps aren't removed (or awarded?) on the first level lost/gained]
#   COMPLETE [replace FOR loops with comprehensions]
#   COMPLETE [view party in methods screen]
#   COMPLETE [convert character sheet party names to buttons]
#   COMPLETE [add a level button in method V]
#   COMPLETE [separate name() and add() methods]
#   COMPLETE [the party member buttons made inactive during name() and order() events]
#   COMPLETE [char_sheet hotkeys only active when char_sheet is active]
#   COMPLETE [add weightedness to the multi-class determination]
#   COMPLETE [get selectclass.py to run faster]
#   COMPLETE [make the race > class determination reversible (class > race)]
#   COMPLETE [get csv checks going at a higher level so in-memory version can be preserved during bulk events}
#   COMPLETE [level range routines for full party & bulk generation]
#   COMPLETE [determine primary display method for full party generation]
#   COMPLETE [deal with 0-level units (currently throwing an error on level checks)]
#   COMPLETE [bulk generation method VI]
#   COMPLETE [need to pack bulk frame and label(s)]
#   COMPLETE [result fields (means, medians, etc)]
#   COMPLETE [right align and background colors in results fields]
#   COMPLETE [rounding in results field]
#   COMPLETE [create a method for generating vulgar fractions]
#   COMPLETE [class & race breakouts, cluster min results]
#   COMPLETE [for hp, age, height and weight, let's have it cluster values at the top and bottom (< 3, > 16)]
#   COMPLETE [void out the two blank buttons in bulk_buttons()]
#   COMPLETE [need to refresh bulk_outcome on result button clicks]
#   COMPLETE [fixed high elf median weight value / bad rstrip on round numbers]
#   COMPLETE [pop out the string tool from self.element_count() (it's now called from the parent)]
#   COMPLETE [pop out the clustering routine (same, though we now need access to the full element count)]
#   COMPLETE [pass sorted dictionaries back to the parent]
#   COMPLETE [pass forward the current center point]
#   COMPLETE [update the clustering method to accept variable center-points]
#   COMPLETE [build placeholder clustering buttons / assign button method(s)]
#   COMPLETE [add expansion/navigation to clustered results]
#   TICKETS:
#       add paths from character sheet to party and vice versa
#       add a save/load function
#       add an auto-reorder button to the view party screen in bulk party gen
#       display selected class in method V
#       display method (I through VI) in all six interim screens
#       up/down arrow hotkeys for race/class selection
#       confirmation window on quit / escape_function()
#       remove case sensitivity from hotkeys
#       pop out the legend in the party comp pie chart to make the fonts match
#       level select option in method VI's generate_individual_character
#       should 0-level characters have a standardized per-race attribute blocks?
#           also they're coming back with bad ages (under 10 y/o)
# 4) figure out storage/equipment fields
#   a)	csv all the armor and weapons
#   b)	weapon proficiencies
#   c)	multi-attack (or does this belong in the class abilities?)
# 5) dual-classing and bards
# 6) stat up 0-level humans, demi-humans & wights
# 7) special abilities
#   a)	spells per level
#   b)	race/class abilities
#   c)	thief-like abilities
#   d)	psionics
#   e)	nonlethal melee
#   f)	miscellaneous ability/resistance definitions
#   g)	languages
#   h)  alignment
# 8) combat engine
#   a) melee weapons
#   b) pummel / grapple / overbear
#   c) psionics
#   d) missile weapons

def clip_surplus_dict(race, attrs, excess):  # nips the tops off attributes above racial maximum
    ord_attrs, rac_max = ['Str', 'Int', 'Wis', 'Dex', 'Con', 'Cha', 'Com'], datalocus.racial_maximums(race)
    temp_excess = dict(zip(ord_attrs, rac_max))
    temp_excess['Wis'] = 25
    for k, v in temp_excess.items():
        temp_excess[k] = attrs[k] - temp_excess[k]
        if temp_excess[k] < 0:
            temp_excess[k] = 0
        attrs[k] -= temp_excess[k]  # trims attributes
        excess[k] += temp_excess[k]  # updates excess
    return


def primary_att(cha_class):                         # returns minimum attributes required for the 10% xp bonus
    return datalocus.xp_bonus_check(cha_class)      # [-1, -1, 16, -1, -1, -1, -1]


def bonus_check(cha_class, atts):  # checks eligibility for 10% xp boost
    minimums = primary_att(cha_class)
    for attribute_score in range(7):
        if atts[attribute_score] < minimums[attribute_score]:
            return False
    return True


def return_xp(ch_class):            # returns the complete list of xp thresholds for the input character class
    xpvalues = datalocus.return_xp(ch_class)
    return xpvalues[0][2:28]        # ['0', '1500', '3000', ...]


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


def flatten(hp_batches):                                        # adds up the elements in nested HP list(s)
    temp = 0
    for hp_batch in hp_batches:
        for value in hp_batch:
            temp += value
    return round(temp/(len(hp_batches)-1))


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
    base, increments = datalocus.return_xp("MeanSum"), datalocus.return_xp("MeanDif")
    base, increments = base[0][1:28], increments[0][2:28]       # note the differing start points
    value = int(base[level]) + roll(int(increments[level]))     # this is to turn increments[level + 1] to [level]
    return value


def impending_mean_xp(xp):                                      # returns the subsequent mean xp threshold (an integer)
    base = datalocus.return_xp("MeanSum")                       # these values are used to increment age in character.py
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
