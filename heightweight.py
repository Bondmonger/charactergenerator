import random
import csv
import datalocus


def _roll(a):  # rolls a single die of "a" sides
    return random.randrange(1, a + 1)


def _rollreps(rolls, die):  # repeatedly calls _roll and sums the results
    result = 0
    for a in range(rolls):
        result += _roll(die)
    return result


def random_gender():
    roll, gender = random.randrange(1, 6), "male"
    if roll == 5:
        gender = "female"
    return gender


def size(race, gender):
    racialsum = datalocus.call_height_weight(race)
    temp, i, gender = _roll(600), 0, 8 * int(gender == "female")  # in other words, "transpose by 8 if female"
    while temp >= racialsum[i]:  # increments through the 5 height tiers for the respective race
        i += 1
    height = racialsum[10 + gender] \
        - _roll(racialsum[11 + gender]) * int(i == 0) \
        - _roll(3 + (racialsum[10 + gender] >= 60)) * int(i == 1) \
        + _roll(3 + (racialsum[10 + gender] >= 60)) * int(i == 3) \
        + _roll(racialsum[12 + gender]) * int(i == 4)
    temp, i, j = _roll(600), 0, 0
    while temp >= racialsum[i]:  # increments through the 5 weight tiers for the respective race
        i += 1
    weight = racialsum[13 + gender] \
        - _rollreps(racialsum[14 + gender], racialsum[15 + gender]) * int(i == 0) \
        - _roll(4 + 4 * (racialsum[13 + gender] >= 100)) * int(i == 1) \
        + _roll(4 + 4 * (racialsum[13 + gender] >= 100)) * int(i == 3) \
        + _rollreps(racialsum[16 + gender], racialsum[17 + gender]) * int(i == 4)
    return [height, weight]

# test = size("Gnome", "male")
# print(test)
