import random
import pandas as pd

temp_dict = {'Race': [], 'Classes': [], 'StrInd': [], 'IntInd': [], 'WisInd': [], 'DexInd': [], 'ConInd': [],
             'ChaInd': [], 'attbonuses': [], 'Eligible': []}
min_df = pd.read_csv("attributemins.csv")  # loads the csv data into memory
min_cols = [0, 1, 2, 3, 4, 5, 6, 10, 26, 27, 28, 29, 30, 31, 32, 70, 71, 73, 74]
min_df = min_df[min_df.columns[min_cols]]  # creates a dataframe using only the specified columns
race_df = min_df[min_df['hum_base'] == "-"]  # creates a dataframe slice of races only


def _roll(a):
    # rolls a single die of "a" sides
    return random.randrange(1, a + 1)


def _dice(r, s):
    # Rolls "r" dice of "s" sides, returning the sum of the three highest values
    results = []
    for a in range(r):
        results.append(_roll(s))
    results.sort(reverse=True)
    return sum(results[0:3])


def string_to_list(string, stringpartition):
    li = list(string.split(stringpartition))
    return li


def multi_mins(characterclass):
    # accepts argument in the form of string 'Fighter/Thief' and returns a list [9, 5, 5, 9, 7, 5]
    temp_x, m, n, final, lug = string_to_list(characterclass, "/"), 0, 0, [0, 0, 0, 0, 0, 0], []
    while n < len(temp_x):
        lug, m = [], 0
        lug.append(min_df.set_index('charclass').loc[temp_x[n], 'strmin'])
        lug.append(min_df.set_index('charclass').loc[temp_x[n], 'intmin'])
        lug.append(min_df.set_index('charclass').loc[temp_x[n], 'wismin'])
        lug.append(min_df.set_index('charclass').loc[temp_x[n], 'dexmin'])
        lug.append(min_df.set_index('charclass').loc[temp_x[n], 'conmin'])
        lug.append(min_df.set_index('charclass').loc[temp_x[n], 'chamin'])
        while m < 6:
            if final[m] < lug[m]:
                final[m] = lug[m]
            m += 1
        n += 1
    return final


def rc_intersect(rc):
    # receives list of eligible races and all legal classes, for example: ['halfling', 'fighter, thief, fighter/thief']
    # then populates temp_dict with Race/Class(es)/minimum attributes for each race/class combination
    i, availableclasses = 0, string_to_list(rc[1], ", ")
    while i < len(availableclasses):
        temp_dict['Race'].append(rc[0])  # adds race
        temp_dict['Classes'].append(availableclasses[i])  # adds class as an x/y string
        # now we convert the x/y character class into a list of minimum attributes using mult_mins()
        class_mins = multi_mins(availableclasses[i])
        # and since the character class(es) are now collapsed into lists of integers, we can use set_index to establish
        # 'charclass' as our index value and compare race minimum against class_mins[x] for each attribute
        temp_dict['StrInd'].append(max(min_df.set_index('charclass').loc[rc[0], 'strmin'], class_mins[0]))
        temp_dict['IntInd'].append(max(min_df.set_index('charclass').loc[rc[0], 'intmin'], class_mins[1]))
        temp_dict['WisInd'].append(max(min_df.set_index('charclass').loc[rc[0], 'wismin'], class_mins[2]))
        temp_dict['DexInd'].append(max(min_df.set_index('charclass').loc[rc[0], 'dexmin'], class_mins[3]))
        temp_dict['ConInd'].append(max(min_df.set_index('charclass').loc[rc[0], 'conmin'], class_mins[4]))
        temp_dict['ChaInd'].append(max(min_df.set_index('charclass').loc[rc[0], 'chamin'], class_mins[5]))
        temp_dict['attbonuses'].append([race_df.set_index('charclass').loc[rc[0], 'strbon'],
                                        race_df.set_index('charclass').loc[rc[0], 'intbon'],
                                        race_df.set_index('charclass').loc[rc[0], 'wisbon'],
                                        race_df.set_index('charclass').loc[rc[0], 'dexbon'],
                                        race_df.set_index('charclass').loc[rc[0], 'conbon'],
                                        race_df.set_index('charclass').loc[rc[0], 'chabon']])
        temp_dict['Eligible'].append('no')
        i += 1
    pass


def eligibility(attributes_dict):
    adjusted_racial_mins = pd.DataFrame()  # creates a new dataframe adjusting racial mins by racial bonus/penalty
    adjusted_racial_mins.loc[:, 'race'] = race_df['charclass']
    adjusted_racial_mins.loc[:, 'stradj'] = race_df['strmin'] - race_df['strbon']
    adjusted_racial_mins.loc[:, 'intadj'] = race_df['intmin'] - race_df['intbon']
    adjusted_racial_mins.loc[:, 'wisadj'] = race_df['wismin'] - race_df['wisbon']
    adjusted_racial_mins.loc[:, 'dexadj'] = race_df['dexmin'] - race_df['dexbon']
    adjusted_racial_mins.loc[:, 'conadj'] = race_df['conmin'] - race_df['conbon']
    adjusted_racial_mins.loc[:, 'chaadj'] = race_df['chamin'] - race_df['chabon']
    adjusted_racial_mins.loc[  # compares current character to adjusted racial minimums
        (attributes_dict['Str'] >= adjusted_racial_mins['stradj']) &
        (attributes_dict['Int'] >= adjusted_racial_mins['intadj']) &
        (attributes_dict['Wis'] >= adjusted_racial_mins['wisadj']) &
        (attributes_dict['Dex'] >= adjusted_racial_mins['dexadj']) &
        (attributes_dict['Con'] >= adjusted_racial_mins['conadj']) &
        (attributes_dict['Cha'] >= adjusted_racial_mins['chaadj']), 'eligible'] = "yes"
    eligibleraces_df = adjusted_racial_mins[adjusted_racial_mins['eligible'] == "yes"]  # creates elig.-race slice
    eligibleraces_list = eligibleraces_df.race.tolist()  # creates a list of currently eligible races
    increment01, increment02 = 0, 0
    while increment01 < len(eligibleraces_list):  # this loop repeatedly calls rc_intersect to populate final_df
        race_cl = [eligibleraces_list[increment01]]
        race_cl.append(min_df.set_index('charclass').loc[race_cl[0], 'classes'])
        rc_intersect(race_cl)
        increment01 += 1
    while increment02 < len(temp_dict['Race']):  # this loop adjusts the aggregated minimums by racial bonus
        temp_dict['StrInd'][increment02] -= temp_dict['attbonuses'][increment02][0]
        temp_dict['IntInd'][increment02] -= temp_dict['attbonuses'][increment02][1]
        temp_dict['WisInd'][increment02] -= temp_dict['attbonuses'][increment02][2]
        temp_dict['DexInd'][increment02] -= temp_dict['attbonuses'][increment02][3]
        temp_dict['ConInd'][increment02] -= temp_dict['attbonuses'][increment02][4]
        temp_dict['ChaInd'][increment02] -= temp_dict['attbonuses'][increment02][5]
        increment02 += 1
    final_df = pd.DataFrame.from_dict(temp_dict)
    final_df.loc[  # compares current character to adjusted class minimums
        (attributes_dict['Str'] >= final_df['StrInd']) &
        (attributes_dict['Int'] >= final_df['IntInd']) &
        (attributes_dict['Wis'] >= final_df['WisInd']) &
        (attributes_dict['Dex'] >= final_df['DexInd']) &
        (attributes_dict['Con'] >= final_df['ConInd']) &
        (attributes_dict['Cha'] >= final_df['ChaInd']), 'Eligible'] = "yes"
    final_df.to_csv(r'E:\DDO\MapGame\Character Generator\pandascsvexport.csv', index=False, header=True)
    eligibleraces_df = final_df[final_df['Eligible'] == "yes"]  # creates elig.-race dataframe slice
    eligibleraces_list = eligibleraces_df.Race.tolist()  # generates list of legal races
    race_list = list(dict.fromkeys(eligibleraces_list))
    race_list.sort()
    eligibleclasses_df = final_df[final_df['Eligible'] == "yes"]  # creates elig.-class dataframe slice
    eligibleclasses_list = eligibleclasses_df.Classes.tolist()  # generates list of legal classes
    class_list = list(dict.fromkeys(eligibleclasses_list))
    class_list.sort()
    final_list = [race_list, class_list]
    print(final_list[0])
    print(final_list[1])
    return final_list


def eligible_races(attributes_dict, char_class):
    adjusted_racial_mins = pd.DataFrame()  # creates a new dataframe adjusting racial mins by racial bonus/penalty
    adjusted_racial_mins.loc[:, 'race'] = race_df['charclass']
    adjusted_racial_mins.loc[:, 'stradj'] = race_df['strmin'] - race_df['strbon']
    adjusted_racial_mins.loc[:, 'intadj'] = race_df['intmin'] - race_df['intbon']
    adjusted_racial_mins.loc[:, 'wisadj'] = race_df['wismin'] - race_df['wisbon']
    adjusted_racial_mins.loc[:, 'dexadj'] = race_df['dexmin'] - race_df['dexbon']
    adjusted_racial_mins.loc[:, 'conadj'] = race_df['conmin'] - race_df['conbon']
    adjusted_racial_mins.loc[:, 'chaadj'] = race_df['chamin'] - race_df['chabon']
    adjusted_racial_mins.loc[  # compares current character to adjusted racial minimums
        (attributes_dict['Str'] >= adjusted_racial_mins['stradj']) &
        (attributes_dict['Int'] >= adjusted_racial_mins['intadj']) &
        (attributes_dict['Wis'] >= adjusted_racial_mins['wisadj']) &
        (attributes_dict['Dex'] >= adjusted_racial_mins['dexadj']) &
        (attributes_dict['Con'] >= adjusted_racial_mins['conadj']) &
        (attributes_dict['Cha'] >= adjusted_racial_mins['chaadj']), 'eligible'] = "yes"
    eligibleraces_df = adjusted_racial_mins[adjusted_racial_mins['eligible'] == "yes"]  # creates elig.-race slice
    eligibleraces_list = eligibleraces_df.race.tolist()  # creates a list of currently eligible races
    increment01, increment02 = 0, 0
    while increment01 < len(eligibleraces_list):  # this loop repeatedly calls rc_intersect to populate final_df
        race_cl = [eligibleraces_list[increment01]]
        race_cl.append(min_df.set_index('charclass').loc[race_cl[0], 'classes'])
        rc_intersect(race_cl)
        increment01 += 1
    while increment02 < len(temp_dict['Race']):  # this loop adjusts the aggregated minimums by racial bonus
        temp_dict['StrInd'][increment02] -= temp_dict['attbonuses'][increment02][0]
        temp_dict['IntInd'][increment02] -= temp_dict['attbonuses'][increment02][1]
        temp_dict['WisInd'][increment02] -= temp_dict['attbonuses'][increment02][2]
        temp_dict['DexInd'][increment02] -= temp_dict['attbonuses'][increment02][3]
        temp_dict['ConInd'][increment02] -= temp_dict['attbonuses'][increment02][4]
        temp_dict['ChaInd'][increment02] -= temp_dict['attbonuses'][increment02][5]
        increment02 += 1
    final_df = pd.DataFrame.from_dict(temp_dict)
    final_df.loc[  # compares current character to adjusted class minimums
        (attributes_dict['Str'] >= final_df['StrInd']) &
        (attributes_dict['Int'] >= final_df['IntInd']) &
        (attributes_dict['Wis'] >= final_df['WisInd']) &
        (attributes_dict['Dex'] >= final_df['DexInd']) &
        (attributes_dict['Con'] >= final_df['ConInd']) &
        (attributes_dict['Cha'] >= final_df['ChaInd']), 'Eligible'] = "yes"
    # final_df.to_csv(r'E:\DDO\MapGame\Character Generator\pandascsvexport.csv', index=False, header=True)
    eligibleraces_df = final_df[final_df['Eligible'] == "yes"]  # creates elig.-race dataframe slice
    testt_df = eligibleraces_df[eligibleraces_df['Classes'] == char_class]
    eligibleraces_list = testt_df.Race.tolist()  # generates list of legal races
    race_list = list(dict.fromkeys(eligibleraces_list))
    race_list.sort()
    # eligibleclasses_df = final_df[final_df['Eligible'] == "yes"]  # creates elig.-class dataframe slice
    eligibleclasses_list = testt_df.Classes.tolist()  # generates list of legal classes
    class_list = list(dict.fromkeys(eligibleclasses_list))
    class_list.sort()
    final_list = [race_list, class_list]
    print(final_list[0])
    print(final_list[1])
    return final_list


# stock_character = {"Str": _dice(4, 6), "Int": _dice(4, 6), "Wis": _dice(4, 6), "Dex": _dice(4, 6), "Con": _dice(4, 6),
#                    "Cha": _dice(4, 6), "Com": _dice(4, 6)}
# print(stock_character)
# eligibility(stock_character)


# attributes_list = race_df.values.tolist()
# raceses = race_df.charclass.tolist()
# print(attributes_list)
# print(raceses)

def random_race():  # returns a random race from the weighted array | WARNING: utilizes a global dataframe (race_df)
    attributes_dict, race_dict = race_df.to_dict(orient='records'), {}  # converts race dataframe into a dictionary
    for a in range(len(attributes_dict)):  # walks through the race dict...
        if attributes_dict[a]['source'] != 'OA':  # ...checks whether current race is sourced from 'OA', and if NOT...
            attributes_dict[a]['weightedprob'] *= 39  # ...increases frequency of current race by 39-fold (+97.5%)
        race_dict[attributes_dict[a]['charclass']] = attributes_dict[a]['weightedprob']  # generates weighted dict
    probability_sum, final_list = sum(race_dict.values()), []
    rand_value, final = random.randrange(0, probability_sum), ''
    for key in race_dict:  # walks through race_dict...
        if rand_value >= race_dict[key]:  # ...checking whether the random integer is greater than the current value...
            rand_value -= race_dict[key]  # ...if not, it subtracts the current value from the random integer...
        elif rand_value >= 0:  # ...and once it arrives at a current value greater than the random integer...
            final = key  # ...it prepares to return the current index string
            rand_value -= race_dict[key]  # ...but continues incrementing through the remainder of the dict
    return final


def random_class(race_is):
    classlist = list(min_df.loc[min_df['charclass'] == race_is]['classes'])
    classlist = string_to_list(classlist[0], ', ')
    single_class, single_dict, multi_class, source_dict = [], {}, [], min_df.to_dict(orient='records')
    for a in classlist:
        if "/" in a:
            multi_class.append(a)
        else:
            single_class.append(a)
    final, multi_rand = '', random.uniform(0, 1)
    multiclass_prob = min_df.set_index('charclass').loc[race_is, 'multiprob']
    if multi_rand > multiclass_prob:
        for a in range(len(single_class)):
            single_dict[single_class[a]] = min_df.set_index('charclass').loc[single_class[a], 'weightedprob']
            if min_df.set_index('charclass').loc[single_class[a], 'source'] != 'OA':
                single_dict[single_class[a]] *= 39
        probability_sum, final_list = sum(single_dict.values()), []
        rand_value = random.randrange(0, probability_sum)
        for key in single_dict:
            if rand_value >= single_dict[key]:
                rand_value -= single_dict[key]
            elif rand_value >= 0:
                final = string_to_list(key, '/')
                rand_value -= single_dict[key]
    else:
        final = string_to_list(random.choice(multi_class),'/')
    return final


# print('single class: ' + str(single_class))
# print('multiclass: '+str(multi_class))
# print('dictionary version of singles:: '+str(single_dict))




# sample_dict = {"atomic wedgies": 4, "noogies": 2, "purple nurples": 1}
# probability_sum, final_list = sum(sample_dict.values()), []
# for a in range(1000):
#     rand_value, final = random.randrange(0, probability_sum), ''
#     for key in sample_dict:
#         if rand_value >= sample_dict[key]:
#             rand_value -= sample_dict[key]
#         elif rand_value >= 0:
#             final = key
#             rand_value -= sample_dict[key]
#     final_list.append(final)
#
#
# print(final_list.count("atomic wedgies"))
# print(final_list.count("noogies"))
# print(final_list.count("purple nurples"))