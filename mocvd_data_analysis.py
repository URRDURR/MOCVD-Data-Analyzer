import os
from os import path
from tkinter import filedialog as fd
import numpy as np
import pandas as pd
from scipy import integrate
import json

# //////////////////////////////////////////////////////
# add a thing that displays the total growth length time
# //////////////////////////////////////////////////////

# returns
def total_slpm_flow(df):

    index_tracker = []

    for i in range(len(df["Date"])):
        if df.loc[i, blocking_valve] == 0 and df.loc[i, bubbler_out_valve] == 1 and df.loc[i, bubbler_in_valve] == 1:
            index_tracker.append(i)

    flow_rate_index = np.squeeze(np.asarray(df.loc[index_tracker, [mass_flow_controler]]))

    total_liters_flow = (integrate.trapezoid(y=flow_rate_index, dx=1)) / 1000

    return total_liters_flow, index_tracker


def liters_to_grams(liters):
    R_TORR_LITERS = 62.3638

    partial_pressure_torr = 10 ** (A - (B / (T + 273.15)))
    mols = (partial_pressure_torr * liters) / (R_TORR_LITERS * (T + 273.15))
    grams = molar_mass * mols

    return grams


# give the locations of all files of a type in a folder
def extract_file_locations(folder_path):
    file_type = "csv"
    # variable holds list of locations of all files of one type in a folder
    file_paths = []

    # creates list of all .{} files in directory
    for i in os.listdir(folder_path):
        if i.endswith(file_type):
            file_paths.append(i)

    # give absolute path of each file in the directory
    for i in range(len(file_paths)):
        file_paths[i] = folder_path + "\\" + file_paths[i]

    return file_paths


PATH_VIA_TERMINAL = False

VERY_BIG_NUMBER = 1_000_000

metal_organic = "AlN"

# compounds = open("compound.json")
# metal_organic_properties = json.load(compounds)[metal_organic]
# compounds.close()

bubbler_in_valve = "DO40"
bubbler_out_valve = "DO38"
blocking_valve = "DO39"
mass_flow_controler = "AI32"
molar_mass = 72.09
A = 8.224
B = 2134.83
T = 18


if PATH_VIA_TERMINAL == True:
    while True:
        location = input("would you like to select a [file] or a [directory]: ")
        if location == "file":
            file_path = fd.askopenfilename()
            print(file_path)
            tag = 0
            break
        elif location == "directory":
            folder_path = fd.askdirectory()
            tag = 1
            break
        else:
            print("please try again")
            continue
else:
    tag = 2
    file_path = r"C:\Users\gma78\Desktop\2024-06-28_S258_Datalog 6-28-2024 3-47-03 PM.csv"
    folder_path = r""
    files = [file_path]

if tag == 0:
    no_of_files = 1
    files = [file_path]
elif tag == 2:
    pass
else:
    files = extract_file_locations(folder_path)

for i in files:
    print(i)
    dataframe = pd.read_csv(i, delimiter=",", parse_dates=True, header=4)

total_liters_flow, index_tracker = total_slpm_flow(dataframe)

print(liters_to_grams(total_liters_flow))

list_string = "\n".join(str(x) for x in index_tracker)

html = (dataframe.style).to_html()
f = open("demofile.html", "w")
f.write(html)
f.close()

f = open("demofile2.txt", "w")
f.write(list_string)
f.close()

print("finished")
