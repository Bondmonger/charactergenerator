import random
import csv


def _roll(a):  # rolls a single die of "a" sides
    return random.randrange(1, a + 1)


def _dice(r, s):  # Rolls "r" dice of "s" sides, returning the sum of the three highest values
    results = []
    for a in range(r):
        results.append(_roll(s))
    results.sort(reverse=True)
    return sum(results[0:3])


def _cruncher(crunch):  # converts ints into floats with small positive decimal values in order to break ties
    crunch = crunch * (1 + (0.001 * random.random()))
    return crunch


def _d6_attributes(b):  # generates list of seven attribute values via b highest six-sided dice
    col_set = []
    for a in range(7):
        col_set.insert(0, _dice(b, 6))
    return col_set


def string_to_list(string, stringpartition):
    separated_elements = list(string.split(stringpartition))
    return separated_elements


def racial_bonus(race, temp):  # racial modifier - temp is the list of attributes
    with open('attrbonuses.csv') as bonuses:
        for row in csv.reader(bonuses):
            if race == row[0]:
                for a in range(7):
                    temp[a] += int(row[a+1])
    return temp


def _minimums(cla_rac):  # returns minimum attribute values by either race or class
    final = []
    with open('attributemins.csv') as mins:
        for row in csv.reader(mins):
            if cla_rac == row[0]:
                for a in range(1, 8):
                    final.append(int(row[a]))
    return final


def racial_maximums(race):  # returns maximum attribute values by race
    final = []
    with open('attributemax.csv') as maxs:
        for row in csv.reader(maxs):
            if row[0] == race:
                for a in range(1, 8):
                    final.append(int(row[a]))
    return final


def clip_surplus(race, attrs):                  # nips the tops off attributes higher than racial maximum
    rac_max, surplus = racial_maximums(race), []
    for a in range(7):
        if attrs[a] <= rac_max[a]:              # if attribute is under the max, place a zero in the surplus list...
            surplus.append(0)
        else:                                   # ...otherwise sets attr to max and places difference in surplus list
            surplus.append(attrs[a] - rac_max[a])
            attrs[a] = rac_max[a]
    return surplus


def _comeliness_bonus(attrs):  # applies charisma bonus to comeliness
    with open('attributevalues.csv') as bonuses:
        for row in csv.reader(bonuses):
            if row[0] == str(attrs[5]):
                attrs[6] += int(row[41])
                pass


def exceptional_str(race):  # returns max percentile strength by race
    with open('attrbonuses.csv') as bonuses:
        for row in csv.reader(bonuses):
            if race == row[0]:
                maximum_exceptional_strength = int(row[8])
    return maximum_exceptional_strength


def archetype(ch_class):  # returns ch_class's archetype
    with open('xpvalues.csv') as archetypes:
        for row in csv.reader(archetypes):
            if ch_class == row[0]:
                class_archetype = row[38]
    return class_archetype


def compute_exstr(attrs, race, excess):     # computes an exceptional strength regardless of class
    archetypes, max_racial_str = [], exceptional_str(race)
    if max_racial_str > 0:                  # rolls an attrs[8] less than or equal to max racial str
        attrs.append(_roll(max_racial_str))
    else:                                   # prevents index error if racial max is a flat 18
        attrs.append(0)
    while attrs[0] > 18:                    # converts strength values above 18 into excess points
        attrs[0] -= 1
        excess[0] += 1
    attrs[7] += excess[0] * 10              # increases percentile points by excess (1 point = +10)
    excess[0] = 0
    if attrs[7] > max_racial_str:           # if percentile is greater than racial max...
        excess[0] = 0
        while attrs[7] > max_racial_str:
            excess[0] += 1                  # ...transfers surplus points back to excess (at 10:1 ratio)...
            attrs[7] -= 10
        attrs[7] = max_racial_str           # ...and sets percentile = racial max
    if attrs[7] > 100:                      # transfers % above 100 back to base strength (at 10:1 ratio, rounding up)
        while attrs[7] > 100:
            attrs[0] += 1
            attrs[7] -= 10
        attrs[7] = 100


def _ua_attr(ch_class):                     # returns a list of method V die counts for called class
    v_values = []
    with open('xpvalues.csv') as ua_dice:
        for row in csv.reader(ua_dice):
            if ch_class == row[0]:
                for a in range(7):
                    v_values.append(int(row[a + 29]))
    return v_values


def _sequencer(ch_class, race):             # sequences a 3d6-to-9d6 for single-class characters
    temp, seq = [], _ua_attr(ch_class)
    for a in range(7):
        temp.insert(a, _dice(seq[a], 6))
    racial_bonus(race, temp)
    return temp


def _multi_sequencer(race, *ch_class):                          # sequences 7 attributes via method V (3d6-to-9d6)
    if len(ch_class[0]) == 1:
        return _sequencer(ch_class[0][0], race)                 # _sequencer() handles single-class characters
    else:
        ninedsix, summed_attrs, final, ordered_list = [], [], [], [*range(3, 10, 1)]
        for a in range(len(ch_class[0])):                       # nests method V values [[9, 3, 5, 7, 8, 6, 4], ...etc]
            ninedsix.append(_ua_attr(ch_class[0][a]))
        for a in range(7):                                      # sums method V values by attribute ([9,7], then [3,4])
            grouped_attrs = []
            for b in range(len(ch_class[0])):
                grouped_attrs.append(ninedsix[b][a])
            grouped_attrs.sort(reverse=True)                    # sorts subgroups for tiebreakers ( 9 + 7 > 8 + 8 )
            summed_attrs.append(sum(grouped_attrs) + 0.1 * grouped_attrs[0] + 0.01 * grouped_attrs[1])
            summed_attrs[a] = _cruncher(summed_attrs[a]) + 10   # applies cruncher to break ties
        ordered_list.reverse()
        for a in range(7):
            summed_attrs[summed_attrs.index(max(summed_attrs))] = ordered_list[a]
        for a in range(7):                                      # rolls up via newly sequenced method V values
            final.append(_dice(summed_attrs[a], 6))
        racial_bonus(race, final)
        return final


def _prioritize(raw_attr, sequence_attr, race):     # _prioritizes raw_attr via sequence_attr
    raw_attr.sort(reverse=True)
    sequence_attr = list(map(_cruncher, sequence_attr))
    for a in range(26, 33):
        sequence_attr[sequence_attr.index(min(sequence_attr))] = a
    for a in range(7):
        sequence_attr[sequence_attr.index(max(sequence_attr))] = raw_attr[a]
    racial_bonus(race, sequence_attr)
    return sequence_attr


def _min_merger(_minimums):                         # merges any number of minimum attribute lists
    final = []
    for a in range(7):
        temp = []
        for b in range(len(_minimums)):
            temp.append(_minimums[b][a])
        final.append(max(temp))
    return final


def _deficit(mins, attrs):                          # returns current attributes minus the minimums
    diff = []
    for a in range(7):
        diff.append(attrs[a] - mins[a])
    return diff


def _positives(diffs):                              # diffs<0 become 0, randomly reduces surplus without going negative
    neg, temp = 0, []
    for ind, att in enumerate(diffs):
        if att > 0:
            temp.append(ind)                        # assembles list of index values for positive diffs, then...
        else:
            neg, diffs[ind] = neg + diffs[ind], 0   # ...sums the negative ones, then...
    for values in range(neg, 0):                    # ...deducts -1s randomly from temp until neg = 0
        index_a = random.choice(temp)
        diffs[index_a] -= 1
        if diffs[index_a] == 0:
            temp.remove(index_a)
    pass


# test_pos = [4, 0, 2, -2, 1, 0, 3]
# _positives(test_pos)
# print(test_pos)

def _re_combine(mins, diffs):                       # sums minimums and "differences," returning combined attributes
    temp = []
    for a in range(7):
        temp.append(mins[a] + diffs[a])
    return temp


def _demote_class(cha_class):                       # drops a class one tier, potentially returning "0-level"
    with open('xpvalues.csv') as characterclasses:
        for row in csv.reader(characterclasses):
            if cha_class == row[0]:
                result = row[37]
    return result


def _minimum_sum(ch_class):  # returns the minimum attribute SUM for a single character class
    classminimums, tempsum = open('attributemins.csv'), 0
    for row in csv.reader(classminimums):
        if ch_class == row[0]:
            for a in range(1, 9):
                tempsum += int(row[a])
    return tempsum


def _maxindex(listofvalues):  # flags the index position of the largest value in a list
    maximum, max_location = 0, 0
    for a, value in enumerate(listofvalues):
        if value > maximum:
            maximum, max_location = value, a
    return max_location


def _demotion(race, ch_classes, raw_atts, merged_mins):  # demotes characters with insufficient attribute points
    racialsum = 0
    with open('attrbonuses.csv') as racial_bonuses:
        for row in csv.reader(racial_bonuses):
            if race == row[0]:
                for a in range(1, 8):
                    racialsum += int(row[a])
    while sum(raw_atts) + racialsum < sum(merged_mins):  # ninja is always the first cut
        minsum = []
        for a in range(len(ch_classes)):
            minsum.append(_cruncher(_minimum_sum((ch_classes[a]))))  # cruncher breaks ties on per-class minimum sums
        # _maxindex(minsum) is the index position of the class with the highest attribute threshold
        newclass = _demote_class(ch_classes[_maxindex(minsum)])  # also removes 0-level results from multi-class chars
        if len(ch_classes) > 1:
            ch_classes.remove(ch_classes[_maxindex(minsum)])
            if newclass == '0-level':
                pass
            else:
                ch_classes.append(newclass)
                ch_classes.sort()
                pass
        else:  # ...otherwise simply demote them to 0-level
            ch_classes.append(newclass)
            ch_classes.remove(ch_classes[0])
            if newclass == '0-level':
                pass
        minlist = list(map(_minimums, ch_classes))  # recalculates the mins and tries again
        minlist.append(_minimums(race))
        newmins, k = _min_merger(minlist), 0
        for a in range(7):
            merged_mins.append(newmins[a])
        del merged_mins[0:7]
    pass

# testclass = ["Ninja", "Bushi"]
# test1 = _demotion('Bamboo Spirit Folk', testclass, [12, 10, 6, 13, 6, 15, 3], [11, 15, 3, 15, 6, 16, 3])
# print(testclass)


def _attr_listdict(attr):
    temp = {'str': attr[0], 'int': attr[1], 'wis': attr[2], 'dex': attr[3], 'con': attr[4], 'cha': attr[5],
            'com': attr[6]}
    if len(attr) > 7:
        temp['exc'] = attr[7]
    print(temp)
    return temp

# temp1 = [14, 15, 12, 15, 12, 16, 5]
# print(_attr_listdict(temp1))


def methodi():  # 4d6, keep the top three dice, user chooses order except for COM (which is locked)
    rawatts = _d6_attributes(4)
    return rawatts


def methodii():  # 3d6 12 times, keep the top seven values totals, user chooses order except for COM (which is locked)
    rawatts = []
    for a in range(12):
        rawatts.append(_dice(3, 6))
    rawatts.sort(reverse=True)
    rawatts = rawatts[0:7]
    random.shuffle(rawatts)
    return rawatts


def methodiii():  # 3d6 6 times for each attribute, order is locked
    rawatts, final = [], []
    for a in range(42):                             # generates a list of 42 3d6 values
        rawatts.append(_dice(3, 6))
    for x in range(7):                              # collects the max from each six-unit chain
        final.append(max(rawatts[x*6:(x+1)*6]))
    return final


def methodiv():  # 3d6 locked, creating 12 full characters, user selects character to keep
    attribs = [[], [], [], [], [], [], [], [], [], [], [], []]
    for a in range(12):
        for b in range(7):
            attribs[a].append(_dice(3, 6))
    return attribs


def methodv(charclass):  # char class is a string, such as "Fighter/Thief"
    attr_names, tempx = ['Str', 'Int', 'Wis', 'Dex', 'Con', 'Cha', 'Com'], string_to_list(charclass, "/")
    tempx, ninedsix = list(map(_ua_attr, tempx)), [*range(3, 10, 1)]    # 9d6 = [3, 4, 5, ... 9]
    combolist, values = tempx[0], [_dice(x, 6) for x in ninedsix]       # tempx = [[9, 3, 4, 7, 8, 6, 5]] if "Fighter"
    for b in range(1, len(tempx)):                                      # triggers only when needed (multi-class)
        for a in range(0, len(tempx[0])):
            combolist[a] = combolist[a] + int(tempx[b][a])
    combolist = list(map(_cruncher, combolist))
    temp_dict = dict(zip(attr_names, combolist))
    temp_dict = {k: v for k, v in sorted(temp_dict.items(), key=lambda item: item[1], reverse=True)}
    orderedatts, ripped_list = temp_dict.keys(), []                     # ripped_list winds up as an ordered list
    values.reverse()                                                    # reverse, not sort (since they're RESULTS)
    final = dict(zip(orderedatts, values))                              # final is the dict version
    for c in attr_names:
        ripped_list.append(final[c])
    return ripped_list


# characterclass = 'Paladin'
# test5 = methodv(characterclass)
# print("method V: ", test5)


def methodvi(race, ch_classes):  # returns modified attributes and an 'excess' list
    raw_atts, mincom = _d6_attributes(4), list(map(_minimums, ch_classes))
    attr_names = ['Str', 'Int', 'Wis', 'Dex', 'Con', 'Cha', 'Com', 'Exc']
    mincom.append(_minimums(race))  # mincon is lists [[classmins1], [classmins2]..., [racemins]]
    merged_mins = _min_merger(mincom)
    _demotion(race, ch_classes, raw_atts, merged_mins)
    if ch_classes[0] == "0-level":
        scrub = [raw_atts, [0, 0, 0, 0, 0, 0, 0]]
        return scrub
    nine_d_six = _multi_sequencer(race, ch_classes)  # rolls up a Method V character and applies racial mods
    ordered_atts = _prioritize(raw_atts, nine_d_six, race)  # substitutes in the 4d6 values and applies racial mods
    surplus_atts = _deficit(merged_mins, ordered_atts)  # flags attributes below race/class minimum(s)
    _positives(surplus_atts)  # redistributes surplus attribute points to negative values
    re_attached = _re_combine(merged_mins, surplus_atts)  # recombines redist. points with merged minimums
    excess = clip_surplus(race, re_attached)  # creates the excess list and nips off attributes over racial caps
    compute_exstr(re_attached, race, excess)
    _comeliness_bonus(re_attached)
    attr_dict = dict(zip(attr_names, re_attached))
    excess_dict = dict(zip(attr_names, excess))
    final = [attr_dict, excess_dict]
    return final


# test1classes = ["Ninja", "Yakuza"]
# test6 = methodvi("Hengeyokai: Crab", test1classes)
# print(test6)
# print(test1classes)


def apply_race_modifiers(race, attribs):  # returns modified attributes and an 'excess' list
    attr_names = ['Str', 'Int', 'Wis', 'Dex', 'Con', 'Cha', 'Com', 'Exc']
    modded_attribs = racial_bonus(race, attribs)
    excess = clip_surplus(race, modded_attribs)
    compute_exstr(modded_attribs, race, excess)
    _comeliness_bonus(modded_attribs)
    attr_dict = dict(zip(attr_names, modded_attribs))
    excess_dict = dict(zip(attr_names, excess))
    final = [attr_dict, excess_dict]
    return final


# not in use
def display_racial_bonuses_i(highlighted_race):         # "High Elf" returns ['', '', '', '+1', '-1', '', '+2']
    list_of_zeroes = [0, 0, 0, 0, 0, 0, 0]
    r_bonuses = racial_bonus(highlighted_race, list_of_zeroes)
    for a in range(len(r_bonuses)):
        if r_bonuses[a] == 0:
            r_bonuses[a] = ""
        else:
            r_bonuses[a] = '{0:+d}'.format(r_bonuses[a])
    return r_bonuses


# not in use
def display_racial_bonuses_ii(highlighted_race):        # "High Elf" returns {'Dex': 1, 'Con': -1, 'Com': 2}
    list_of_zeroes, display_list = [0, 0, 0, 0, 0, 0, 0], []
    att_names = ["Str", "Int", "Wis", "Dex", "Con", "Cha", "Com"]
    r_bonuses = racial_bonus(highlighted_race, list_of_zeroes)
    r_bondict = dict(zip(att_names, r_bonuses))
    final = {k: v for k, v in r_bondict.items() if v != 0}
    return final


test_display = "High Elf"

print(racial_bonus(test_display, [0, 0, 0, 0, 0, 0, 0]))
display_racial_bonuses_i(test_display)
display_racial_bonuses_ii(test_display)

# test7 = apply_race_modifiers("Grugach", [20, 12, 12, 12, 12, 12, 12])
# print(test7)
