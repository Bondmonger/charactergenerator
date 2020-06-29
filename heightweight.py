import random
import csv


def _roll(a):
    # rolls a single die of "a" sides
    return random.randrange(1, a + 1)


def _rollreps(rolls, die):
    # repeatedly calls _roll and sums the results
    i, result = 0, 0
    while i < rolls:
        result += _roll(die)
        i += 1
    return result


def size(race, gender):
    sizevalues, racialsum, i = open('attrbonuses.csv'), [], 0
    for row in csv.reader(sizevalues):
        if race == row[0]:
            while i < 26:
                racialsum.append(int(row[i+18]))
                i += 1
    temp, i, gender = _roll(600), 0, 8 * int(gender == "female")
    while temp >= racialsum[i]:
        i += 1
    height = racialsum[10 + gender] \
             - _roll(racialsum[11 + gender]) * int(i==0) \
             - _roll(3 + (racialsum[10 + gender] >= 60 )) * int(i==1) \
             + _roll(3 + (racialsum[10 + gender] >= 60 )) * int(i==3) \
             + _roll(racialsum[12 + gender]) * int(i==4)
    temp, i, j = _roll(600), 0, 0
    while temp >= racialsum[i]:
        i += 1
    weight = racialsum[13 + gender] \
             - _rollreps(racialsum[14 + gender], racialsum[15 + gender]) * int(i==0) \
             - _roll(4 + 4 * (racialsum[13 + gender] >= 100 )) * int(i==1) \
             + _roll(4 + 4 * (racialsum[13 + gender] >= 100 )) * int(i==3) \
             + _rollreps(racialsum[16 + gender], racialsum[17 + gender]) * int(i==4)
    return [height, weight]

# test = size("Human", "female")
# print(test)