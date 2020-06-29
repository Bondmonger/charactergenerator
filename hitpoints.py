import random
import csv


def roll(a):
    # rolls a single die of "a" sides
    return random.randrange(1, a + 1)


def call_hp(ch_class):
    # returns hpcalc data for a single class ("Fighter") in order to generate_hp(). The values are:
    # [1HD, 1#rolls, 1bonus, midLevelHD, midCap, maxIncrements, max_con_bonus, bonus_multiplier, fixed_bonus]
    characterclasses, result, i = open('xpvalues.csv'), [], 0
    for row in csv.reader(characterclasses):
        if ch_class == row[0]:
            while i < 9:
                result.append(int(row[39+i]))
                i += 1
    return result


def hp_compute_first(hpcalcs):
    # calculates 1st level hitpoints
    i, hitpoints = 0, 0
    while i < hpcalcs[1]:
        hitpoints += roll(hpcalcs[0]) + (hpcalcs[2])
        i += 1
    return hitpoints


def hp_compute_mid(hpcalcs, hp, level):
    # calculates mid level hit points and adds them to list hp
    # hpcalcs[8] is the +1 per level that Wu-jen get
    i = 1
    while i < level:
        if i < hpcalcs[4]:
            hp.append(roll(hpcalcs[3])+hpcalcs[8])
        else:
            return i
        i += 1
    return i


def hp_compute_top(hpcalcs, hp, level):
    # calculates end game hit points and adds them to list hp
    i = hpcalcs[4]
    while i < level:
        hp.append(hpcalcs[5])
        i += 1


def con_bonus(hitpoints, hpcalcs, con):
    attr_bonuses, i, j, bonus, temp = open('attributevalues.csv'), 0, 0, 0, []
    # grabs the root con bonus from attributevalue.csv and the class info at hpcalcs
    for row in csv.reader(attr_bonuses):
        if str(con) == row[0]:
            bonus = int(row[29])
    # creates a list of con bonuses, one for each class, and then
    # trims down to each class's con max (where necessary)
    while i < len(hpcalcs):
        if bonus > hpcalcs[i][6]:
            temp.append(hpcalcs[i][6])
        else:
            temp.append(bonus)
        # hpcalcs[i][7] is the con multiplier (barbarians are x2)
        temp[i] *= hpcalcs[i][7]
        i += 1
    # this takes each class's con bonus and multiplies it by the number of eligible levels
    while j < len(hpcalcs):
        bonus = hpcalcs[j][1] + len(hitpoints[j]) - 1
        if bonus > hpcalcs[j][4]:
            bonus = hpcalcs[j][4]
        temp[j] *= bonus
        j += 1
    hitpoints.append(temp)
    return i


def generate_hp(ch_class, levels, con):
    # generates hit points for new characters of level "levels",
    # returning nested lists showing hit points rolled for each
    # class/level [[fig1, fig2, fig3], [mu1, mu2], [th1, th2, th3, th4]]
    i, j, num_classes, hpcalcs, hp, final = \
    0, 0, len(ch_class), [], [], []
    while i < num_classes:
        hpcalcs.append(call_hp(ch_class[i]))
        i += 1
    while j < num_classes:
        hp.append(hp_compute_first(hpcalcs[j]))
        if levels[j] > 1:
            hp_compute_mid(hpcalcs[j], hp, levels[j])
        if levels[j] > hpcalcs[j][4]:
            hp_compute_top(hpcalcs[j], hp, levels[j])
        final.append(hp)
        hp = []
        j += 1
    con_bonus(final, hpcalcs, con)
    if "Ninja" in ch_class:
        k = 0
        while k < len(ch_class):
            final[len(ch_class)][k] *= 2
            k += 1
    return final


# test = generate_hp(["Barbarian", "Monk"], [13, 13], 6)
# print(test)

