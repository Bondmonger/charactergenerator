import random
import csv


def roll(a):  # rolls a single die of "a" sides
    return random.randrange(1, a + 1)


def call_hp(ch_class):  # returns hpcalc data for a single class ("Fighter") in order to generate_hp()
    character_classes, result = open('xpvalues.csv'), []
    for row in csv.reader(character_classes):
        if ch_class == row[0]:
            for a in range(9):
                result.append(int(row[39+a]))
    return result  # [1HD, 1#rolls, 1bon, midLevelHD, midCap, maxIncrs, max_con_bonus, bonus_multiplier, fixed_bonus]


def hp_compute_first(hpcalcs):  # calculates starter hit points: roundup(maximum_hp/3)
    hitpoints = 0
    for a in range(hpcalcs[1]):
        hitpoints += roll(hpcalcs[0]) + (hpcalcs[2])
    return hitpoints


def hp_compute_mid(hpcalcs, hp, level, incoming_level=1):  # calculates mid-level hit points and adds them to list hp
    for a in range(incoming_level, level):  # incoming level needs to be the number of hp rolls for class [a]
        if a < hpcalcs[4]:
            hp.append(roll(hpcalcs[3])+hpcalcs[8])  # hpcalcs[8] is the +1 per level that Wu-jen get
        else:
            pass


def hp_compute_top(hpcalcs, hp, level):  # calculates name-level hit points and adds them to list hp
    for a in range(hpcalcs[4], level):
        if a > len(hp):
            hp.append(hpcalcs[5])


def con_bonus(hitpoints, hpcalcs, con):  # grabs con bonus info from attributevalue.csv and class info from hpcalcs
    attr_bonuses, bonus, temp = open('attributevalues.csv'), 0, []
    for row in csv.reader(attr_bonuses):  # creates a list of con bonuses, one for each class
        if str(con) == row[0]:
            bonus = int(row[29])
    for a in range(len(hpcalcs)):
        if bonus > hpcalcs[a][6]:  # trims bonus for non-fighter types
            temp.append(hpcalcs[a][6])
        else:
            temp.append(bonus)
        temp[a] *= hpcalcs[a][7]  # hpcalcs[i][7] is the con multiplier (barbarians get double bonus hp)
    for a in range(len(hpcalcs)):  # takes each class's con bonus and multiplies it by number of levels
        bonus = hpcalcs[a][1] + len(hitpoints[a]) - 1
        if bonus > hpcalcs[a][4]:
            bonus = hpcalcs[a][4]
        temp[a] *= bonus
    hitpoints.append(temp)
    pass


def generate_hp(ch_class, levels, con):  # generates new character hp of level "levels", returns nested lists
    number_of_classes, hpcalcs, hp, final = len(ch_class), [], [], []
    for a in range(number_of_classes):
        hpcalcs.append(call_hp(ch_class[a]))
    for a in range(number_of_classes):
        hp.append(hp_compute_first(hpcalcs[a]))
        if levels[a] > 1:
            hp_compute_mid(hpcalcs[a], hp, levels[a])
        if levels[a] > hpcalcs[a][4]:
            hp_compute_top(hpcalcs[a], hp, levels[a])
        final.append(hp)
        hp = []
    con_bonus(final, hpcalcs, con)
    if "Ninja" in ch_class:  # ninjas don't get a con bonus but receive double con bonus for their alternative class
        for a in range(number_of_classes):
            final[number_of_classes][a] *= 2
    return final  # [[fig1, fig2, fig3], [mu1, mu2], [th1, th2, th3, th4], [figcon, mucon, thcon]]


# test = generate_hp(["Barbarian", "Monk"], [5, 5], 17)
# print(test)
