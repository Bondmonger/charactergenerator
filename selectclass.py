import random
import pandas as pd
import time
import csv
import datalocus
from functools import lru_cache


def min_merger(_minimums):                                      # used by combinator()
    final = []
    for att in range(6):
        temp = []
        for minimum_set in _minimums:
            temp.append(minimum_set[att])
        final.append(max(temp))
    return final


# a, b, c = [10, 14, 10, 16, 8, 8], [7, 7, 13, 13, 7, 7], [12, 12, 12, 12, 12, 12]
# print(min_merger([a, b, c]))

def string_to_list(string, stringpartition):    # accepts a single string and converts it to a list
    li = list(string.split(stringpartition))
    return li


def list_to_string(list_of_classes):            # accepts a list of lists, like [[Fighter, Thief], [Cleric], ...]
    string_version = []
    for element in list_of_classes:             # this also folds each string_term into a tuple (for later sorting)
        string_term = ''
        for term in element:
            string_term = string_term + term + '/'
        string_term = string_term.rstrip('/')
        string_version.append(tuple([string_term]))
    return string_version


# sample_list = [['Aquatic Elf', 'Fighter'], ['Aquatic Elf', 'Thief'], ['Aquatic Elf', 'Fighter', 'Thief']]
# print('test list_to_string', list_to_string(sample_list))


@lru_cache(maxsize=1000)
def combinator():
    races_and_classes, final, output = [], [], []
    with open('attributemins.csv') as mins:
        for row in csv.reader(mins):
            if row[71] != '-' and row[71] != 'classes':         # eliminates class rows and header (we only want races)
                temp_race = row[0]                              # assigns persistent race value for upcoming FOR loop
                class_list = string_to_list(row[71], ', ')      # converts classes-permitted-by-race STRING to LIST...
                for a in class_list:
                    carrier_list = [temp_race]
                    carrier_list.extend(string_to_list(a, '/'))
                    races_and_classes.append(carrier_list)      # ...and adds it to the permissible combos list
    for permissible_combo in races_and_classes:                 # permissible combo: ['High Elf', 'Fighter', 'Thief']
        collected_mins, racial_bonus = [], []
        for a, race_cl in enumerate(permissible_combo):
            minimums_list = datalocus.minimums(race_cl)         # assigns minimums and bonuses
            racial_bonus = datalocus.racial_attribute_bonus(race_cl) if a == 0 else racial_bonus
            collected_mins.append(minimums_list)                # appends minimum_list(s) to temporary list
        combinated = min_merger(collected_mins)                 # merges minimums / max value at each position
        combin_bonus = [x - y for x, y in zip(combinated, racial_bonus)]
        final.append(combin_bonus)                              # collects the modified minimums in final
    output.append(races_and_classes)
    output.append(final)                                        # returns minimums - racial_bonus
    return output


# start = time.time()
# for a in range(10):
#     combinator()
# end = time.time()
# print("combinator runtime:", end - start)


@lru_cache(maxsize=1000)
def other_combinator():
    races_and_classes, final, output = [], [], []
    source_list, frequency_list, multifreq_list, class_dict = [], [], [], {}
    with open('attributemins.csv') as mins:
        for row in csv.reader(mins):
            if row[71] != '-':                              # looking only at races (passing classes to ELSE)
                temp_race = row[0]                          # assigns persistent race value for upcoming FOR loop
                class_list = string_to_list(row[71], ', ')  # separates permissible class STRING to LIST
                for a in class_list[1:]:                    # skips the header...
                    carrier_list = [temp_race]
                    carrier_list.extend(string_to_list(a, '/'))
                    races_and_classes.append(carrier_list)  # ...and converts each character class STRING to LIST
                    source_list.append(row[70])
                    frequency_list.append(row[73])
                    multifreq_list.append(row[74])
            else:
                class_dict[row[0]] = [row[70], row[73]]     # populates class_dict with sources & frequencies
    perm_prob, perm_source = [], []
    for a, permissible_combo in enumerate(races_and_classes):
        collected_mins, racial_bonus = [], []               # permissible combo: ['High Elf', 'Fighter', 'Thief']
        for b, race_cl in enumerate(permissible_combo):
            minimums_list = datalocus.minimums(race_cl)     # assigns minimums and bonuses
            racial_bonus = datalocus.racial_attribute_bonus(race_cl) if b == 0 else racial_bonus
            collected_mins.append(minimums_list)            # appends minimum_list(s) to temporary list
        combinated = min_merger(collected_mins)             # merges minimums / max value at each position
        combin_bonus = [x - y for x, y in zip(combinated, racial_bonus)]
        final.append(combin_bonus)                          # collects the modified minimums in final
        temp_prob, temp_source = [frequency_list[a]], [source_list[a]]
        for b in races_and_classes[a][1:]:                  # we already placed the races in the temp LISTS
            temp_source.append(class_dict[b][0])            # this goes back to the class_dict we made in the...
            temp_prob.append(class_dict[b][1])              # ...first FOR loop
        perm_source.append(temp_source)
        perm_prob.append(temp_prob)
    output.append(races_and_classes)                        # [['Aquatic Elf', 'Fighter'], ['Aquatic Elf', 'Thief'],
    output.append(final)                                    # [[9, 8, 5, 6, 8, 8], [5, 8, 3, 8, 7, 8], [9, 8, 5, 8,
    output.append(multifreq_list)                           # ['0.85', '0.85', '0.85', '0', '0', '0.85', '0.85',
    output.append(perm_source)                              # [['PH', 'PH'], ['PH', 'PH'], ['PH', 'PH', 'PH'],
    output.append(perm_prob)                                # [['1', '84'], ['1', '26'], ['1', '84', '26'], ['18',
    return output


# start = time.time()
# # print(other_combinator())
# for a in range(100):
#     other_combinator()
# end = time.time()
# print("other combinator runtime:", end - start)


class IsEligible:
    def __init__(self):
        temp_elig = combinator()
        self.complete_race_class_list = temp_elig[0]
        self.minimums = temp_elig[1]
        self.combined_eligibility = []
        self.eligible_races, self.eligible_classes, self.eligible_races_classes = [], [], []
        return

    def check_eligibility(self, subject):               # subject is an ordered LIST of attrs [8, 14, 8, 11, 15, 9]
        eligibility_check = []
        for a, min_attribs in enumerate(self.minimums):
            for b in range(6):
                if subject[b] < min_attribs[b]:
                    eligibility_check.append(False)     # assigns FALSE if a minimum is not met
                    break
                if b == 5:
                    eligibility_check.append(True)      # assigns TRUE if all minimums are met
        self.combined_eligibility = eligibility_check   # adds eligibility check to the IsEligible object

    def eligible(self, attributes):
        self.check_eligibility(attributes)
        temp_output, clashes, rashes = [], [], []
        for a, bool_value in enumerate(self.combined_eligibility):
            if bool_value:
                temp_output.append(self.complete_race_class_list[a])
        for a in temp_output:
            tempo = tuple(a)
            rashes.append(tempo[:1])
            clashes.append(tempo[1:])
        # print('temp_output:', temp_output, '\n')    # this is our randomized value here and in filtered_elig
        clashes, rashes = list_to_string(list(set(clashes))), list(set(rashes))
        clashes.sort(), rashes.sort()
        class_output, race_output = [], []
        for a in clashes:
            class_output.append(a[0])
        for a in rashes:
            race_output.append(a[0])
        self.eligible_races = race_output
        self.eligible_classes = class_output
        self.eligible_races_classes = temp_output

    def filtered_eligibility(self, attributes, race_class_input):
        self.check_eligibility(attributes)
        temp_bool_insert = self.combined_eligibility[:]
        stringed_race_class = []
        for a in self.complete_race_class_list:
            temp_race_class, string_term = [a[0]], ''
            for b in range(len(a[1:])):
                string_term = string_term + a[b+1] + '/'
            string_term = string_term.rstrip('/')
            temp_race_class.append(string_term)
            stringed_race_class.append(temp_race_class)
        for bool_a in range(len(self.combined_eligibility)):
            if self.combined_eligibility[bool_a]:
                if race_class_input not in stringed_race_class[bool_a]:
                    temp_bool_insert[bool_a] = False
        temp_output, clashes, rashes = [], [], []           # from here on out it's identical to eligible_output()...
        for a in range(len(self.combined_eligibility)):
            if temp_bool_insert[a]:                         # ...except we're looking at the temp_bool_insert
                temp_output.append(self.complete_race_class_list[a])
        for a in temp_output:
            tempo = tuple(a)
            rashes.append(tempo[:1])
            clashes.append(tempo[1:])
        clashes, rashes = list_to_string(list(set(clashes))), list(set(rashes))
        clashes.sort(), rashes.sort()
        class_output, race_output = [], []
        for a in clashes:
            class_output.append(a[0])
        for a in rashes:
            race_output.append(a[0])
        self.eligible_races = race_output
        self.eligible_classes = class_output
        self.eligible_races_classes = temp_output

    def random_from_elig_rc(self):
        if len(self.eligible_races_classes) == 0:
            print("there are no eligible classes / 0-level output")  # should we randomize race for these?
            return
        else:
            rand_index = random.randrange(len(self.eligible_races_classes))
            return self.eligible_races_classes[rand_index]


# something = IsEligible()
# attribies = [15, 5, 3, 16, 5, 5]
# something.eligible(attribies)
# ajawndong = something.eligible_races
# print('unfiltered eligibility: ', something.__dict__['eligible_races_classes'])  # 10, 10, 10,...
# something.filtered_eligibility(attribies, 'Human')
# print('eligible_classes:         ', something.__dict__['eligible_classes'], '\n')


# NOT IN USE (generates a list of all permissible race/class combos
def list_o_classes():
    races_and_classes = []
    with open('attributemins.csv') as mins:
        for row in csv.reader(mins):
            if row[71] != '-' and row[71] != 'classes':         # eliminates class rows and header (we only want races)
                temp_race = row[0]                              # assigns persistent race value for upcoming FOR loop
                class_list = string_to_list(row[71], ', ')      # converts classes-permitted-by-race STRING to LIST...
                for a in class_list:
                    carrier_list = [temp_race]
                    carrier_list.extend(string_to_list(a, '/'))
                    races_and_classes.append(carrier_list)      # ...and adds it to the permissible combos list
    return races_and_classes                                    # [['Aquatic Elf', 'Fighter'], ['Aquatic Elf', Thief'],.


# test_chump = list_o_classes()
# print('test chump: ', test_chump)


@lru_cache(maxsize=10)
def race_class_data():
    min_df = pd.read_csv("attributemins.csv")  # loads the csv data into memory
    min_cols = [0, 1, 2, 3, 4, 5, 6, 10, 26, 27, 28, 29, 30, 31, 32, 70, 71, 73, 74]
    # 70 - source (PH, UA or OA)
    # 71 - permissible classes string (including multi-classes, races-only, classes get a placeholder '-')
    # 73 - frequency (an integer from 1 (drow, aquatic elf, bard, grugach) to 360 (human)
    # 74 - multiclass proportion (races-only, a fraction from 0 to 0.85, classes are left blank '')
    min_df = min_df[min_df.columns[min_cols]]  # creates a dataframe using only the specified columns
    min_df['modifiedfreq'] = min_df['weightedprob']
    mask = min_df['source'] != 'OA'
    min_df.loc[mask, 'modifiedfreq'] = min_df['weightedprob'] * 39
    return min_df


@lru_cache(maxsize=10)
def race_only_data():
    min_df = race_class_data()
    race_df = min_df[min_df['hum_base'] == "-"]  # creates a dataframe slice of races only
    return race_df


def random_race():  # returns a random race from the weighted array
    race_df = race_only_data()
    attributes_dict = race_df.to_dict(orient='records')
    race_dict = {}  # converts race dataframe into a dictionary
    for race_class in attributes_dict:  # walks through the race dict...
        race_dict[race_class['charclass']] = race_class['modifiedfreq']  # generates weighted dict
    return random.choices(list(race_dict.keys()), weights=race_dict.values(), k=1)[0]


# not in use
@lru_cache(maxsize=150)         # min_df has 19 fields: charclass, hum_base, source, classes, weightedprob & multiprob
def single_class_dicts(race):   # charclass is race and class, hum_base separates r/c, classes is pre-race eligible...
    min_df = race_class_data()  # ...wp = human: 360, mp = elf: 0.85 (plus rac/cla minimums and racial bonuses
    classlist = list(min_df.loc[min_df['charclass'] == race]['classes'])    # grabs cs 'classes' field for current race
    classlist, multi_class, single_class = string_to_list(classlist[0], ', '), [], []   # converts cs string to list
    for a in classlist:
        multi_class.append(a) if "/" in a else single_class.append(a)       # parses classes into multi- and single-
    multiclass_prob, single_dict = min_df.set_index('charclass').loc[race, 'multiprob'], {}
    for ch_class in single_class:
        single_dict[ch_class] = min_df.set_index('charclass').loc[ch_class, 'modifiedfreq']
    final = {"single": single_dict, "multiclass": multi_class, "multiclass_prob": multiclass_prob}
    return final


@lru_cache(maxsize=150)
def temp_class_dicts(race):    # charclass is race and class, hum_base separates r/c, classes is pre-race eligible...
    min_df = race_class_data()  # ...wp = human: 360, mp = elf: 0.85 (plus rac/cla minimums and racial bonuses
    classlist = list(min_df.loc[min_df['charclass'] == race]['classes'])    # grabs cs 'classes' field for current race
    classlist, multi_class, single_class = string_to_list(classlist[0], ', '), [], []   # converts cs string to list
    for a in classlist:
        multi_class.append(a) if "/" in a else single_class.append(a)       # parses classes into multi- and single-
    multiclass_prob, single_dict, temp_df = min_df.set_index('charclass').loc[race, 'multiprob'], {}, min_df.copy()
    temp_df = temp_df[temp_df['hum_base'] != "-"]   # otherwise it inexplicably adds Hengeyokai: Monkey as class option
    temp_df['eligible'] = temp_df['charclass'].apply(lambda x: any([k in x for k in single_class]))     # boolean elig.
    temp_df = temp_df.loc[temp_df['eligible'], ['charclass', 'modifiedfreq']]
    single_dict = dict(temp_df.values)
    final = {"single": single_dict, "multiclass": multi_class, "multiclass_prob": multiclass_prob}
    return final    # no faster than single_class_dicts()


def random_class(race_is):              # accepts 'High Elf', returns ['Ranger']
    multi_rand, proportions = random.uniform(0, 1), temp_class_dicts(race_is)
    if multi_rand > proportions["multiclass_prob"]:     # if single-class, select from the proportional dictionary
        return random.choices(list(proportions["single"].keys()), weights=proportions["single"].values(), k=1)
        # probability_sum, proportional_sum = sum(proportions["single_dict"].values()), 0
        # rand_value = random.randrange(0, probability_sum)
        # for key in proportions["single_dict"]:
        #     proportional_sum += proportions["single_dict"][key]
        #     if proportional_sum >= rand_value:
        #         return string_to_list(key, '/')
    else:                                               # otherwise pick at random from the multi-class list
        return string_to_list(random.choice(proportions["multiclass"]), '/')
