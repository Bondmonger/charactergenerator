import random
import pandas as pd
import time
import csv


def min_merger(_minimums):                                      # used by combinator()
    final = []
    for att in range(6):
        temp = []
        for b in range(len(_minimums)):
            temp.append(_minimums[b][att])
        final.append(max(temp))
    return final


def string_to_list(string, stringpartition):    # accepts a single string and converts it to a list
    li = list(string.split(stringpartition))
    return li


def list_to_string(list_of_classes):            # accepts a list of lists, like [[Fighter, Thief], [Cleric], ...]
    string_version = []
    for element in list_of_classes:             # this also folds each string_term into a tuple (for later sorting)
        string_term = ''
        for b in range(len(element)):
            string_term = string_term + element[b] + '/'
        string_term = string_term.rstrip('/')
        string_version.append(tuple([string_term]))
    return string_version


# sample_list = [['Aquatic Elf', 'Fighter'], ['Aquatic Elf', 'Thief'], ['Aquatic Elf', 'Fighter', 'Thief']]
# print('test list_to_string', list_to_string(sample_list))


def combinator():
    races_and_classes, final, output = [], [], []
    with open('attributemins.csv') as mins:
        for row in csv.reader(mins):
            if row[71] != '-' and row[71] != 'classes':         # eliminates class rows and header (we only want races)
                temp_race = row[0]                              # assigns persistent race value for upcoming FOR loop
                class_list = string_to_list(row[71], ', ')      # separates permissible class STRING to LIST
                for a in class_list:
                    carrier_list = [temp_race]
                    carrier_list.extend(string_to_list(a, '/'))
                    races_and_classes.append(carrier_list)      # ...and converts each character class STRING to LIST
        for a in races_and_classes:
            collected_mins = []
            for b in range(len(a)):                             # walks down the list of races and classes
                minimums_list = []
                mins.seek(0)                                    # resets the incrementing pointer
                for row in csv.reader(mins):
                    if a[b] == row[0]:                          # if the entry matches Column A...
                        for c in range(1, 7):                   # ...populates minimums_list with Columns B through G
                            minimums_list.append(int(row[c]))
                        if b == 0:                              # skips the column header (row 1), then...
                            racial_bonus = []
                            for d in range(26, 32):             # ...populates racial_bonus with columns AA through AF
                                racial_bonus.append(int(row[d]))
                collected_mins.append(minimums_list)            # appends minimum_list(s) to temporary list
            combinated = min_merger(collected_mins)             # merges minimums / max value at each position
            combin_bonus = [x - y for x, y in zip(combinated, racial_bonus)]
            final.append(combin_bonus)                          # collects the modified minimums in final
        output.append(races_and_classes)
        output.append(final)                                    # returns minimums - racial_bonus
    return output


def other_combinator():
    races_and_classes, final, output = [], [], []
    source_list, frequency_list, multifreq_list, class_dict = [], [], [], {}
    with open('attributemins.csv') as mins:
        for row in csv.reader(mins):
            if row[71] != '-':                                  # looking only at races (passing classes to ELSE)
                temp_race = row[0]                              # assigns persistent race value for upcoming FOR loop
                class_list = string_to_list(row[71], ', ')      # separates permissible class STRING to LIST
                for a in class_list[1:]:                        # skips the header...
                    carrier_list = [temp_race]
                    carrier_list.extend(string_to_list(a, '/'))
                    races_and_classes.append(carrier_list)      # ...and converts each character class STRING to LIST
                    source_list.append(row[70])
                    frequency_list.append(row[73])
                    multifreq_list.append(row[74])
            else:
                class_dict[row[0]] = [row[70], row[73]]         # populates class_dict with sources & frequencies
        for a in races_and_classes:
            collected_mins = []
            for b in range(len(a)):                             # walks down the list of races and classes
                minimums_list = []
                mins.seek(0)                                    # resets the incrementing pointer
                for row in csv.reader(mins):
                    if a[b] == row[0]:                          # if the entry matches Column A...
                        for c in range(1, 7):                   # ...populates minimums_list with Columns B through G
                            minimums_list.append(int(row[c]))
                        if b == 0:                              # skips the column header (row 1), then...
                            racial_bonus = []
                            for d in range(26, 32):             # ...populates racial_bonus with columns AA through AF
                                racial_bonus.append(int(row[d]))
                collected_mins.append(minimums_list)            # appends minimum_list(s) to temporary list
            combinated = min_merger(collected_mins)             # merges minimums / max value at each position
            combin_bonus = [x - y for x, y in zip(combinated, racial_bonus)]
            final.append(combin_bonus)                          # collects the modified minimums in final
        perm_prob, perm_source = [], []
        for a in range(len(races_and_classes)):                 # now for each race/class combo
            temp_prob, temp_source = [frequency_list[a]], [source_list[a]]
            for b in races_and_classes[a][1:]:                  # we already placed the races in the temp LISTS,...
                temp_source.append(class_dict[b][0])            # ...this goes back to the class_dict we made in the...
                temp_prob.append(class_dict[b][1])              # ...first FOR loop
            perm_source.append(temp_source)
            perm_prob.append(temp_prob)
        output.append(races_and_classes)                        # [['Aquatic Elf', 'Fighter'], ['Aquatic Elf', 'Thief'],
        output.append(final)                                    # [[9, 8, 5, 6, 8, 8], [5, 8, 3, 8, 7, 8], [9, 8, 5, 8,
        output.append(multifreq_list)                           # ['0.85', '0.85', '0.85', '0', '0', '0.85', '0.85',
        output.append(perm_source)                              # [['PH', 'PH'], ['PH', 'PH'], ['PH', 'PH', 'PH'],
        output.append(perm_prob)                                # [['1', '84'], ['1', '26'], ['1', '84', '26'], ['18',
        print('class_dict: ', class_dict, '\n')
    return output


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
        for a in range(len(self.complete_race_class_list)):
            for b in range(6):
                if subject[b] < self.minimums[a][b]:
                    eligibility_check.append(False)     # assigns FALSE if a minimum is not met
                    break
                if b == 5:
                    eligibility_check.append(True)      # assigns TRUE if all minimums are met
        self.combined_eligibility = eligibility_check   # appends eligibility check to the IsEligible object

    def eligible(self, attributes):
        self.check_eligibility(attributes)
        temp_output, clashes, rashes = [], [], []
        for a in range(len(self.combined_eligibility)):
            if self.combined_eligibility[a]:
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
            print("there are no eligible classes / 0-level output")  # we should randomize race for these
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


# NOT IN USE (but don't erase it - this generates a list of all permissible race/class combos
def list_o_classes():
    races_and_classes = []
    with open('attributemins.csv') as mins:
        for row in csv.reader(mins):
            if row[71] != '-':                              # eliminates class rows (we only want races)
                temp_race = row[0]                              # assigns persistent race value for use in FOR loop
                class_list = string_to_list(row[71], ', ')      # separates permissible class STRING into LIST
                for a in class_list[1:]:                        # skips the header...
                    carrier_list = [temp_race]
                    carrier_list.extend(string_to_list(a, '/'))
                    races_and_classes.append(carrier_list)      # and divideseach char class element into a LIST
    return races_and_classes                                    # [['Aquatic Elf', 'Fighter'], ['Aquatic Elf', Thief'],.


# test_chump = list_o_classes()
# print('test chump: ', test_chump)


min_df = pd.read_csv("attributemins.csv")  # loads the csv data into memory
min_cols = [0, 1, 2, 3, 4, 5, 6, 10, 26, 27, 28, 29, 30, 31, 32, 70, 71, 73, 74]
# 70 - source (PH, UA or OA)
# 71 - permissible classes (including multi-classes, races-only, classes get a placeholder '-')
# 73 - frequency (an integer from 1 (drow, aquatic elf, bard, grugach) to 360 (human)
# 74 - multiclass proportion (races-only, a fraction from 0 to 0.85, classes are left blank '')
min_df = min_df[min_df.columns[min_cols]]  # creates a dataframe using only the specified columns
race_df = min_df[min_df['hum_base'] == "-"]  # creates a dataframe slice of races only


def random_race():  # returns a random race from the weighted array | WARNING: utilizes a global dataframe (race_df)
    attributes_dict, race_dict = race_df.to_dict(orient='records'), {}  # converts race dataframe into a dictionary
    print('race_df as dict:           ', attributes_dict)
    for a in range(len(attributes_dict)):  # walks through the race dict...
        if attributes_dict[a]['source'] != 'OA':  # ...checks whether current race is sourced from 'OA', and if NOT...
            attributes_dict[a]['weightedprob'] *= 39  # ...increases frequency of current race by 39-fold (97.5%)
        race_dict[attributes_dict[a]['charclass']] = attributes_dict[a]['weightedprob']  # generates weighted dict
    probability_sum, final_list = sum(race_dict.values()), []
    rand_value, final = random.randrange(0, probability_sum), ''
    for key in race_dict:  # walks through race_dict...
        if rand_value >= race_dict[key]:  # ...checking whether the random integer is greater than the current value...
            rand_value -= race_dict[key]  # ...if not, it subtracts the current value from the random integer...
        elif rand_value >= 0:  # ...and once it arrives at a current value greater than the random integer...
            final = key  # ...it prepares to return the current index string
            rand_value -= race_dict[key]  # ...but continues iterating through the the dict
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
        final = string_to_list(random.choice(multi_class), '/')
    return final


# start = time.time()
# combinator()
# end = time.time()
# print("combinator speed check:", end - start)

start = time.time()
chubrub = other_combinator()
end = time.time()
print("othercombinator speed check:", end - start)

print('\nrace & class: ', chubrub[0])
print('modified min: ', chubrub[1])
print('multicl prob: ', chubrub[2])
print("source man'l: ", chubrub[3])
print('frequency:    ', chubrub[4], '\n')


start = time.time()

testjawn = IsEligible()
print(testjawn.__dict__['complete_race_class_list'])
print(testjawn.__dict__['minimums'])

nerf = [6, 8, 5, 8, 8, 8]

testjawn.check_eligibility(nerf)
print(testjawn.__dict__['combined_eligibility'], '\n')

testjawn.eligible(nerf)
print('complete_race_class_list: ', testjawn.__dict__['complete_race_class_list'])
print('eligible_races_classes:   ', testjawn.__dict__['eligible_races_classes'])
print('eligible_races:           ', testjawn.__dict__['eligible_races'])
print('eligible_classes:         ', testjawn.__dict__['eligible_classes'])
print('selection:                ', testjawn.random_from_elig_rc(), '\n')

testjawn.filtered_eligibility(nerf, 'Thief')
print('complete_race_class_list: ', testjawn.__dict__['complete_race_class_list'])
print('eligible_races_classes:   ', testjawn.__dict__['eligible_races_classes'])
print('eligible_races:           ', testjawn.__dict__['eligible_races'])
print('eligible_classes:         ', testjawn.__dict__['eligible_classes'])
print('selection:                ', testjawn.random_from_elig_rc(), '\n')

end = time.time()
print("class speed check:", end - start)


start = time.time()
print('\nrandom race:               ', random_race())
end = time.time()
print('random race timing:        ', end - start, '\n')

start = time.time()
print('random race & class:       ', random_class(random_race()))
end = time.time()
print('random race & class timing:', end - start)
