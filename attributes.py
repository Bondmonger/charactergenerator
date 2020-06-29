import random
import csv


def _roll(a):
    # rolls a single die of "a" sides
    return random.randrange(1, a + 1)


def _dice(r, s):
    # Rolls "r" dice of "s" sides, returning the sum of
    # the three highest values
    loosey, j = [], 0
    while j < r:
        loosey.append(_roll(s))
        j += 1
    loosey.sort()
    return loosey[-1] + loosey[-2] + loosey[-3]


def _cruncher(crunch):
    # converts ints into floats with small positive 
    # decimal values in order to break ties
    crunch = crunch * (1 + (0.001 * random.random()))
    return crunch


def _puffer(puff):
    # adds 10 to a value, to clear space for tiebreakers
    puff = puff + 10
    return puff


def _4d6_attributes(b):
    # generates list of seven attribute values via "b"
    # highest six-sided dice
    col_set, k = [], 0
    while k < 7:
        col_set.insert(0, _dice(b, 6))
        k += 1
    else:
        return col_set


def _racial_bonus(race, temp):
    # racial modifier - "temp" is the list of attributes
    bonuses, i = open('attrbonuses.csv'), 0
    for row in csv.reader(bonuses):
        if race == row[0]:
            while i < 7:
                temp[i] += int(row[i+1])
                i += 1
    return temp


def _minimums(cla_rac):
    # returns minimum attribute values for either race or class
    temp, mins, i = [], open('attributemins.csv'), 1
    for row in csv.reader(mins):
        if cla_rac == row[0]:
            while i < 8:
                temp.append(int(row[i]))
                i += 1
    return temp


def _racial_maximums(race):
    # WARNING: THIS FUNCTION IS ONLY CHECKING THE FIRST TEN CHARACTERS
    # OF BOTH CLASS NAME AND THE FIRST COLUMN IN ATTRIBUTEMAX.CSV - I
    # did this so I could get away with one hengeyokai entry in that
    # spreadsheet, but it's probably a bad idea.  max attribute values
    # by race
    temp, maxs, i, race = [], open('attributemax.csv'), 1, race[0:10]
    for row in csv.reader(maxs):
        if row[0][0:10] == race:
            while i < 8:
                temp.append(int(row[i]))
                i += 1
    return temp


def _clip_surplus(race, attrs):
    # nips the tops off attributes higher than racial maximum
    i, rac_max, surplus = 0, _racial_maximums(race), []
    while i < 7:
        if attrs[i] <= rac_max[i]:
            surplus.append(0)
        else:
            surplus.append(attrs[i] - rac_max[i])
            attrs[i] = rac_max[i]
        i += 1
    return surplus


def _comeliness_bonus(attrs):
    # applies charisma bonus to comeliness
    if attrs[5] < 4:
        attrs[6] -= 5
        pass
    elif attrs[5] < 6:
        attrs[6] -= 3
        pass
    elif attrs[5] < 9:
        attrs[6] -= 1
        pass
    elif attrs[5] < 13:
        attrs[6] += 0
        pass
    elif attrs[5] < 16:
        attrs[6] += 1
        pass
    elif attrs[5] < 18:
        attrs[6] += 2
        pass
    elif attrs[5] == 18:
        attrs[6] += 3
        pass
    elif attrs[5] > 18:
        attrs[6] += 5
        pass


def _exceptional_str(race):
    # returns max percentile strength; note that halflings are capped
    # at zero, which we would want to have drop down to a flat 18 (for
    # instance if they roll the max (17) and then landed in the mature
    # age category)
    bonuses, i = open('attrbonuses.csv'), 0
    for row in csv.reader(bonuses):
        if race == row[0]:
            temp = int(row[8])
    return temp


def _compute_exstr(attrs, race, ch_class, excess):
    # computes exceptional strength on fighter types, calling
    # _exceptional_str() for racial limits, then increasing
    # values by 10pts for each excess point
    if attrs[0] == 18:
        if "Fighter" in ch_class or "Bushi" in ch_class \
        or "Sohei" in ch_class or "Kensai" in ch_class \
        or "Oriental Barbarian" in ch_class or "Samurai" \
        in ch_class or "Barbarian" in ch_class or \
        "Ranger" in ch_class or "Paladin" in ch_class or \
        "Cavalier" in ch_class or "Bard" in ch_class:
            attrs.append(_roll(_exceptional_str(race)))
            while excess[0] > 0:
                if attrs[8] < _exceptional_str(race):
                    excess[0] -= 1
                    attrs[8] += 10
                    if attrs[8] > _exceptional_str(race):
                        attrs[8] = _exceptional_str(race)
                        if attrs[8] == 101:
                            attrs[0] = 19
                        return
                else:
                    pass
        else:
            pass
    else:
        pass


def _ua_attr(ch_class):
    # returns a list of method V die values for called class
    ua_dice, i, temp = open('xpvalues.csv'), 0, []
    for row in csv.reader(ua_dice):
        if ch_class == row[0]:
            while i < 7:
                temp.append(int(row[i + 29]))
                i += 1
    return temp


def _sequencer(ch_class, race):
    # sequences a 3d6-to-9d6 for single-class characters
    temp, seq, i = [], _ua_attr(ch_class), 0
    while i < 7:
        temp.insert(i, _dice(seq[i], 6))
        i += 1
    _racial_bonus(race, temp)
    return temp


def _multi_sequencer(race, *ch_class):
    # if a single character class is passed in, calls _sequencer and
    # returns a sequenced 3d6-to-9d6.  If two or three classes are
    # passed in then it goes on to the else function.  There are a
    # lot of variables here so let's go through them:
    # nineDsix: list of all relevant 9d6s to this character
    # numclasses: number of elements in ch_class
    # ordered_list: [3,4,5,6,7,8,9]
    # temp1: holds items from like positions in nineDsix (that
    #   is, it sums up all the strengths, then all the ints,
    #   etc, then passes along sums of each like position to
    #   temp2)
    # temp2: receives sums from temp1 - also tallies first level
    #   of tiebreakers (two highest elements of each position
    #   from temp1 - thus (9 + 7) > (8+8))
    # temp3: first applies coin flip tiebreaker to values in
    #   temp2, then replaces cumulative/tiebroken values with
    #   corresponding 9d6 values from ordered_list
    # final: performs a set of 9d6s using the hierarchy in temp3,
    #   then applies racial bonuses
    if len(ch_class[0]) == 1:
       return _sequencer(ch_class[0][0], race)
    else:
        nineDsix, temp1, temp2, temp3, final, i, j \
        = [], [], [], [], [], 0, 0
        num_classes, ordered_list = len(ch_class[0]), [*range(3, 10, 1)]
        while i < num_classes:
            # generates nests containing the method V values (for multiclass)
            # [[9, 3, 5, 7, 8, 6, 4], [7, 4, 9, 5, 8, 6, 3]]
            nineDsix.insert(0, _ua_attr(ch_class[0][i]))
            i += 1
        i, current_val = 0, 0
        while i < 7:
            while j < num_classes:
                # generates a temp1 list containing method V values for the
                # current "i" attribute, so first [9, 7], then [3, 4], etc
                temp1.insert(i, nineDsix[j][i])
                j += 1
            temp1.sort(), temp1.reverse()
            temp2.insert(i, sum(temp1) + 0.1 * temp1[0] + \
                         0.01 * temp1[1])
            j, temp1 = 0, []
            i += 1
        # cruncher to break ties, puffer (+10) to keep the keep all 7 temp2
        # values north of the ordered_list (UA) values
        temp3 = list(map(_cruncher, temp2))
        temp3 = list(map(_puffer, temp3))
        ordered_list.reverse()
        while j < 7:
            temp3[temp3.index(max(temp3))] = ordered_list[j]
            j += 1
        i = 0
        while i < 7:            
            final.insert(i, _dice(temp3[i], 6))
            i += 1
        _racial_bonus(race, final)
        return final


def _prioritize(raw_attr, sequence_attr, race):
    # orders a raw_attr list (4d6s) and _prioritizes those values
    # via a sequence_attr (method V) list, cruncher() to break ties
    raw_attr.sort(), raw_attr.reverse()
    sequence_attr = list(map(_cruncher, sequence_attr))
    i, j = 26, 0
    while i < 33:
       sequence_attr[sequence_attr.index(min(sequence_attr))] = i
       i += 1
    while j < 7:
        sequence_attr[sequence_attr.index(max(sequence_attr))] = raw_attr[j]
        j += 1
    _racial_bonus(race, sequence_attr)
    return sequence_attr


def _min_merger(_minimums):
    # merges any number of minimum attribute lists
    temp, i, j, rcelements, holder = \
    [], 0, 0, len(_minimums), []
    while i < 7:
        while j < rcelements:
            temp.append(_minimums[j][i])
            j += 1
        holder.append(max(temp))
        i += 1
        j, temp = 0, []
    return holder


def _deficit(mins, atts):
    # returns current attributes minus the minimums
    i, diff = 0, []
    while i < 7:
        diff.append(atts[i] - mins[i])
        i += 1
    return diff


def _positives(diffs):
    # converts negative differences into zeroes, randomly
    # extracting points from positive values without 
    # driving them negative
    i, neg, temp = 0, 0, []
    for att in diffs:
        if att > 0:
            temp.append(i)
        else:
            neg, diffs[i] = neg + diffs[i], 0
        i += 1
    while neg < 0:
        a = random.choice(temp)
        diffs[a] -= 1
        if diffs[a] == 0:
            temp.remove(a)
        neg += 1
    pass


def _re_combine(mins, diffs):
    # sums minimums and "differences," returning combined attributes
    i, temp = 0, []
    while i < 7:
        temp.append(mins[i] + diffs[i])
        i += 1
    return temp


def _clean_up(char):
    # combines attributes into a list
    i, temp, final = 0, [], []
    while i < 7:
        temp.append(char[i])
        i += 1
    if len(char) == 9:
        temp.append(char[8])
    final.append(temp)
    final.append(char[7])
    return final


def _demote_class(cha_class):
    # drops a class one tier, potentially returning "0-level"
    characterclasses, result = open('xpvalues.csv'), 0
    for row in csv.reader(characterclasses):
        if cha_class == row[0]:
            result = row[37]
    return result


def _minimum_sum(ch_class):
    # returns the minimum attribute SUM for a single character class
    classminimums, i, tempsum = open('attributemins.csv'), 1, 0
    for row in csv.reader(classminimums):
        if ch_class == row[0]:
            while i < 9:
                tempsum += int(row[i])
                i += 1
    return tempsum


def _maxindex(listofvalues):
    # flags the position of the largest value in a list
    maximum, maxlocation, i = 0, 0, 0
    for i, value in enumerate(listofvalues):
        if value > maximum:
            maximum = value
            maxlocation = i
        i += 1
    return maxlocation


def _demotion(race, ch_classes, raw_atts, merged_mins):
    # performs class demotion (Paladin into Fighter, etc) on characters
    # who do not have enough attribute points to meet their race/class mins
    racialbonuses, racialsum, i = open('attrbonuses.csv'), 0, 1
    for row in csv.reader(racialbonuses):
        if race == row[0]:
            while i < 8:
                racialsum += int(row[i])
                i += 1
    while sum(raw_atts) + racialsum < sum(merged_mins):
        # ninja is always the first cut
        j, minsum = 0, []
        while j < len(ch_classes):
            # cruncher to break ties on the per-class sums (minimum attributes)
            minsum.append(_cruncher(_minimum_sum((ch_classes[j]))))
            j += 1
        # _maxindex(minsum) is the index position of the class with the highest attribute threshold
        newclass = _demote_class(ch_classes[_maxindex(minsum)])
        # if multiclassed, remove any 0-level results from string...
        if len(ch_classes) > 1:
            ch_classes.remove(ch_classes[_maxindex(minsum)])
            if newclass == '0-level':
                pass
            else:
                ch_classes.append(newclass)
                ch_classes.sort()
                pass
        # ...otherwise simply demote them to 0-level
        else:
            ch_classes.append(newclass)
            ch_classes.remove(ch_classes[0])
            if newclass == '0-level':
                return
        # recalculate the minimums and try again
        minlist = list(map(_minimums, ch_classes))
        minlist.append(_minimums(race))
        newmins, k = _min_merger(minlist), 0
        while k < 7:
            merged_mins.append(newmins[k])
            k += 1
        del merged_mins[0:7]
    pass


# testclass = ["Ninja", "Bushi"]
# test1 = _demotion('Hengeyokai: Crab', testclass, [12, 10, 3, 13, 6, 15, 3], [11, 15, 3, 15, 6, 16, 3])
# print(testclass)


def _attr_listdict(attr):
    temp = {}
    temp['str'] = attr[0]
    temp['int'] = attr[1]
    temp['wis'] = attr[2]
    temp['dex'] = attr[3]
    temp['con'] = attr[4]
    temp['cha'] = attr[5]
    temp['com'] = attr[6]
    if len(attr) > 7:
        temp['exc'] = attr[7]
    print(temp)
    return temp

# temp1 = [14, 15, 12, 15, 12, 16, 5]
# print(_attr_listdict(temp1))


def methodVI(race, ch_classes):
    # returns modified attributes and an 'excess' list
    raw_atts = _4d6_attributes(4)
    mincom = list(map(_minimums, ch_classes))
    mincom.append(_minimums(race))
    # mincon is lists [[classmins1], [classmins2]..., [racemins]]
    merged_mins = _min_merger(mincom)
    _demotion(race, ch_classes, raw_atts, merged_mins)
    if ch_classes[0] == "0-level":
        scrub = []
        scrub.append(raw_atts)
        scrub.append([0,0,0,0,0,0,0])
        return scrub
    nine_d_six = _multi_sequencer(race, ch_classes)
    ordered_atts = _prioritize(raw_atts, nine_d_six, race)
    surplus_atts = _deficit(merged_mins, ordered_atts)
    _positives(surplus_atts)
    re_attached = _re_combine(merged_mins, surplus_atts)
    excess = _clip_surplus(race, re_attached)
    re_attached.append(excess)
    _compute_exstr(re_attached, race, ch_classes, excess)
    _comeliness_bonus(re_attached)
    final = _clean_up(re_attached)
    return final

# test1classes = ["Ninja", "Yakuza"]
# test1 = methodVI("Hengeyokai: Crab", test1classes)
# print(test1)
# print(test1classes)

