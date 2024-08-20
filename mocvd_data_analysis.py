import os
from tkinter import filedialog as fd
import numpy as np
import pandas as pd
from scipy import integrate
import json
from pint import UnitRegistry
import re

# returns the total number of liters that flow out of the bubbler
def total_slpm_flow(df):

    temp = 18

    index_tracker = []

    for i in range(len(df["Date"])):
        if df.loc[i, blocking_valve] == 0 and df.loc[i, bubbler_out_valve] == 1 and df.loc[i, bubbler_in_valve] == 1:
            index_tracker.append(i)

    # array of the pressure level (Torr)
    pressure_array = np.squeeze(np.asarray(df.loc[index_tracker, [pressure_flow_controler]]))

    # array of the rate of flow (standard cubic centimeters per minute)
    flow_rate_array = np.squeeze(
        np.asarray(df.loc[index_tracker, [mass_flow_controler]])
    )  # NOTE: this may be wrong in how this is converted/intergrated, please check with David

    # array of the rate of flow (standard liters per second)
    for i in range(len(flow_rate_array)):
        flow_rate_array[i] /= 60 * 1000

    # Turned into regular liters per second
    for i in range(len(flow_rate_array)):
        flow_rate_array[i] = flow_rate_array[i] * (((t + 273.15) / (273.15)) * (760 / pressure_array[i]))

    # Numericaly integrates into total real liters
    total_liters_flow = integrate.trapezoid(y=flow_rate_array, dx=1)

    return total_liters_flow, index_tracker


# Assuming carrier gas is saturated immediately, calculates grams of metal oxide contained
def liters_to_grams(liters):
    # gas constant in units "Torr" and "Liters"
    R_TORR_LITERS = 62.3638

    # calculates partial pressure and applies (pv)/(rt) = n to get mols (factor of 2 added to account for tmal being dimer)
    # NOTE: need to add a check for this in non dimer compounds (or just double the molar mass)
    partial_pressure_torr = 10 ** (A - (B / (t + 273.15)))
    mols = (partial_pressure_torr * liters) / (R_TORR_LITERS * (t + 273.15))

    print("ack",mols/9.25)

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


PATH_VIA_TERMINAL = True

metal_organic = "TMAl"

# compounds = open("compound.json")
# metal_organic_properties = json.load(compounds)[metal_organic]
# compounds.close()

bubbler_in_valve = "DO40"
bubbler_out_valve = "DO38"
blocking_valve = "DO39"
mass_flow_controler = "AI32"
pressure_flow_controler = "AI33"
molar_mass = 72.09 * 2
A = 8.224
B = 2134.83
t = -10

# Selects all the files to be read
if PATH_VIA_TERMINAL == True:
    while True:
        location = input("would you like to select a file [1] or a directory [2]: ")
        if location == "1":
            file_path = fd.askopenfilename()
            files = [file_path]
            break
        elif location == "2":
            folder_path = fd.askdirectory()
            files = extract_file_locations(folder_path)
            break
        else:
            print("please try again")
            continue
else:
    file_path = r"C:/Users/gma78/Desktop/Excels/2024-06-28_S258_Datalog 6-28-2024 3-47-03 PM.csv"
    files = [file_path]

grams_total = 0
time_total = 0

grams_by_run = []
time_by_run = []
name = []

# Calculates the total time on and liters outputed of the given metal oxide/bubbler
for i in files:
    print(i)
    dataframe = pd.read_csv(i, delimiter=",", parse_dates=True, header=4)
    total_flow_liters, index_tracker = total_slpm_flow(dataframe)

    total_grams = liters_to_grams(total_flow_liters)

    grams_total += total_grams
    time_total += len(index_tracker)

    grams_by_run.append(float(total_grams))
    time_by_run.append(len(index_tracker))

    designator = re.split("/|\\\\", i)
    print(designator)
    designator = ((designator)[-1].split(" "))[0]

    name.append(designator)

print(grams_by_run)
print(time_by_run)


by_run = pd.DataFrame(
    {
        "Name": name,
        "Grams by run": grams_by_run,
        "Time by run": time_by_run,
    }
)

totals = pd.DataFrame(
    {
        "Grams total": grams_total,
        "Time total": time_total,
    },
    index=[0],
)

result = pd.concat([by_run, totals], axis=1)

print("Result:\n", result)

result.to_csv("file2.csv", index=False)

print("Grams in last run:")
# print("Grams total of", metal_organic, ":", grams_total)

print("total time run for", metal_organic, ":", time_total)

# list_string = "\n".join(str(x) for x in index_tracker)

# html = (dataframe.style).to_html()
# f = open("demofile.html", "w")
# f.write(html)
# f.close()

# f = open("demofile2.txt", "w")
# f.write(list_string)
# f.close()

print("Finished")
