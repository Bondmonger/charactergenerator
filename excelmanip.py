from functools import lru_cache
import pandas as pd
import os
import csv

# creates a file "test.csv" at D:/Hockey/NHLBrackets/
# path needs to point to the directory with all the brackets (no subdirectories, no other files)
# all brackets need to be .xlsx (throws an error if it hits an .xls, .csv, .gsheet, etc)
# will deal with integers or strings in series length predictions, but not empty spaces after the number (Chase)

current_dict, final_dict, path = {}, {}, r"D:/Hockey/NHLBrackets/2024/"


@lru_cache(maxsize=35)
def abbrev(full_name):
    full_length = {"Hurricane": "Hur", "Blue Jackets": "Cbj", "Devils": "Dev", "Islanders": "Isl", "Rangers": "Ran",
                   "Flyers": "Fly", "Penguins": "Pen", "Capitals": "Cap", "Bruins": "Bru", "Red Wings": "Red",
                   "Panthers": "Pan", "Canadiens": "Hab", "Senators": "Sen", "Lightning": "Ltg", "Leafs": "Lfs",
                   "Coyotes": "Coy", "Blackhawks": "Hwk", "Avalanche": "Avs", "Stars": "Str", "Wild": "Wld",
                   "Predators": "Prd", "Blues": "Blu", "Jets": "Jet", "Ducks": "Dck", "Flames": "Flm", "Oilers": "Oil",
                   "Kings": "Kng", "Sharks": "Shk", "Kraken": "Krk", "Canucks": "Can", "Golden Knights": "Vgk",
                   "Sabres": "Sab"}
    return full_length[full_name]


for filename in os.listdir(path):
    f, series_length = ''.join([path, filename]), 0
    loc_bloc0 = [1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 4, 4, 7, 7, 10]
    loc_bloc1 = [4, 8, 12, 16, 20, 24, 28, 32, 6, 14, 22, 30, 10, 26, 18]
    loc_bloc2 = [4, 4, 4, 4, 4, 4, 4, 4, 7, 7, 7, 7, 10, 10, 10]
    loc_bloc3 = [4, 5, 12, 13, 20, 21, 28, 29, 8, 9, 24, 25, 16, 17, 22]
    if os.path.isfile(f):
        print(filename.split("_", 1)[0])
        current_df = pd.read_excel(f)                           # loads .xlsx
        for a, (kcol, krow, vcol, vrow) in enumerate(zip(loc_bloc0, loc_bloc1, loc_bloc2, loc_bloc3)):
            if isinstance(current_df.iat[krow, kcol], str):     # if "length" is a string, trim to final character...
                series_length = int(current_df.iat[krow, kcol][-1:])
            else:                                               # if "length" is an integer, leave as is
                series_length = current_df.iat[krow, kcol]
            current_dict[a] = (abbrev(current_df.iat[vrow, vcol][3:]), series_length)   # add pick & length to dict
        if isinstance(current_df.iat[29, 10], str):             # add goals-scored tiebreaker to the end
            current_dict[len(loc_bloc0)] = int(current_df.iat[29, 10].split(" = ", 3)[1])
        else:
            current_dict[len(loc_bloc0)] = current_df.iat[29, 10]
        # print(current_dict)
        final_dict[filename.split("_", 1)[0]] = current_dict.copy()     # ...and add entire current_dict to final_dict


with open('D:/Hockey/NHLBrackets/test.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    for key, selection in final_dict.items():
        data = [key]
        temp_dict = {k: selection[k] for k in selection.keys() - {15}}
        for k, element in temp_dict.items():
            data.append(element[0])
        data.append('')
        for k, element in temp_dict.items():
            data.append(element[1])
        data.append('')
        data.append(selection[15])
        writer.writerow(data)
