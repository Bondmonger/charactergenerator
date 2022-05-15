import random
import time
import datalocus


def _roll(a):  # rolls a single die of "a" sides
    return random.randrange(1, a + 1)


def _merge_variables(race, ch_class):               # returns three-item lists [base_age, #ofrolls, #ofsides]
    temp, final, number_of_classes = [], [0, 0, 0], len(ch_class)
    for a in range(number_of_classes):
        temp.append(datalocus.age_variables(race, ch_class[a]))
    for a in range(number_of_classes):
        if final[0] < temp[a][0]:
            final[0] = temp[a][0]
    for a in range(number_of_classes):
        if final[1] * final[2] < temp[a][1] * temp[a][2]:
            final[1], final[2] = temp[a][1], temp[a][2]
    return final


def _natural_death(race):                                                                   # accepts ('Human')
    temp = random.choice([0, 0, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4])      # returns (96)
    var_value, age_thresholds = [8, 4, 6, 10, 20], datalocus.age_thresholds(race)
    # this calculates the age-span for the relevant category to determine which age_modifier to apply
    term = age_thresholds[4+round(temp/3)] - age_thresholds[3+round(temp/3)]
    age_modifier = 1 * int(term < 100) + 10 * int(100 <= term <= 250) + 20 * int(term > 250)
    # this formula computes the base age corresponding with the temp value
    temp_base = int(age_thresholds[round((temp+6.5)/2)]) + int(temp == 0 or temp == 2)
    # this formula computes the die roll, span modifier and operator corresponding with the temp value
    temp_roll = (_roll(var_value[temp]) * age_modifier + _roll(age_modifier) - 1) * (temp % 2 * -2 + 1)
    return temp_base + temp_roll


# for i in range(100):
#     temp_death = _natural_death("Human")
#     print(temp_death)


def generate_age(race, ch_class, level):
    temp, final, attr_names = _merge_variables(race, ch_class), [], ['Str', 'Int', 'Wis', 'Dex', 'Con', 'Cha', 'Com']
    age = temp[0]
    for a in range(temp[1]):
        age += _roll(temp[2])
    final.append(age - 1 + level)
    final.append(datalocus.age_cat(race, age)[0])
    final.append(datalocus.age_cat(race, age)[1])
    final.append(dict(zip(attr_names, datalocus.age_adj(final[1]))))
    final[3]['Exc'] = 0
    final.append(_natural_death(race))
    return final


# start = time.time()
# testrace = "Korobokuru"
# testclass = ["Shukenja"]
# a = generate_age(testrace, testclass, 2)
# print(a)
# end = time.time()
# print('duration:', end-start)
