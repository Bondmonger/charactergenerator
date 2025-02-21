import random
import datalocus


def roll(a):  # rolls a single die of "a" sides
    return random.randrange(1, a + 1)


def hp_compute_first(hp_data):  # calculates starter hit points: roundup(maximum_hp/3)
    die_size, num_dice, modifier = hp_data[0], hp_data[1], hp_data[2]
    return sum(roll(die_size) + modifier for _ in range(num_dice))


def hp_compute_mid(hpcalcs, hp, level, incoming_level=1):  # calculates mid-level hit points and adds them to list hp
    for a in range(incoming_level, level):  # incoming level needs to be the number of hp rolls for class [a]
        if a < hpcalcs[4]:
            hp.append(roll(hpcalcs[3])+hpcalcs[8])  # hpcalcs[8] is the +1 per level that Wu-jen get


def hp_compute_top(hpcalcs, hp, level):  # calculates name-level hit points and adds them to list hp
    for a in range(hpcalcs[4], level+1):
        if a > len(hp):
            hp.append(hpcalcs[5])


def con_bonus(hitpoints, hpcalcs, con):  # grabs con bonus info from attributevalue.csv and class info from hpcalcs
    bonus, transp = datalocus.con_hpbonus(con), []
    for a, class_con_cap in enumerate(hpcalcs):
        temp = class_con_cap[6] if bonus > class_con_cap[6] else bonus   # non-fighters capped at +2
        temp *= class_con_cap[7]                                 # barbarians receive 2x bonus
        multiplier = class_con_cap[1] + len(hitpoints[a]) - 1    # tallies up hit dice (not levels!)...
        if multiplier > class_con_cap[4]:
            multiplier = class_con_cap[4]                        # ...restricts multiplier to non-name levels, then...
        transp.append(temp * multiplier)                         # ...multiplies con bonus by non-name levels
    hitpoints.append(transp)                                     # [figcon, mucon, thcon]


def generate_hp(ch_class, levels, con):     # generates hp for character of level "levels", returns nested lists
    hpcalcs, hp, final = [], [], []
    for character_class in ch_class:
        hpcalcs.append(datalocus.call_hp(character_class))
    for a, csv_data in enumerate(hpcalcs):
        hp.append(hp_compute_first(csv_data))
        if levels[a] > 1:
            hp_compute_mid(csv_data, hp, levels[a])
        if levels[a] > csv_data[4]:
            hp_compute_top(csv_data, hp, levels[a])
        final.append(hp)
        hp = []
    con_bonus(final, hpcalcs, con)
    if "Ninja" in ch_class:             # ninjas don't receive con bonus but get x2 con bonus for their primary class
        for a, character_class in enumerate(ch_class):
            final[-1][a] *= 2
    return final                        # [[fig1, fig2, fig3], [mu1, mu2], [th1, th2, th3, th4], [figcon, mucon, thcon]]


# test = generate_hp(["Barbarian", "Monk"], [5, 5], 17)
# print(test)
