import os
from tkinter import filedialog as fd
import numpy as np
import pandas as pd
from scipy import integrate
import re

STANDARD_PRESSURE_TORR = 760
STANDARD_TEMPERATURE_KELVIN = 273.15


# returns the total number of liters that flow out of the bubbler
def slpm_to_liters(df, organometal):
    # partial_pressure_torr = 10 ** (
    #     organometal.a - (organometal.b / (organometal.t + STANDARD_TEMPERATURE_KELVIN))
    # )

    index_tracker = []

    for i in range(len(df["Date"])):
        if (
            df.loc[i, organometal.blocking_valve] == 0
            and df.loc[i, organometal.bubbler_out_valve] == 1
            and df.loc[i, organometal.bubbler_in_valve] == 1
        ):
            index_tracker.append(i)
    # NOTE: Assumsumption here is that if the valve opens multiple times, the slight increase in total volume calculated due to placing the 1st closing
    # by the second oppening of the valve, and then integrating over that area, is so negligible that it is unnecessary to change the calculation to remove this

    # array of the pressure level (Torr)
    pressure_array = np.squeeze(
        np.asarray(df.loc[index_tracker, [organometal.pressure_flow_controler]])
    )

    # array of the rate of flow (standard cubic centimeters per minute)
    flow_rate_array = np.squeeze(
        np.asarray(df.loc[index_tracker, [organometal.mass_flow_controler]])
    )  # NOTE: this may be wrong in how this is converted/intergrated, please check with David

    # array of the rate of flow (standard liters per second)
    for i in range(len(flow_rate_array)):
        flow_rate_array[i] /= 60 * 1000

    # Turned into regular liters per second
    for i in range(len(flow_rate_array)):
        flow_rate_array[i] = flow_rate_array[i] * (
            (
                (organometal.t + STANDARD_TEMPERATURE_KELVIN)
                / (STANDARD_TEMPERATURE_KELVIN)
            )
            * (STANDARD_PRESSURE_TORR / (pressure_array[i] - organometal.partial_pressure_torr()))
        )

    # Numericaly integrates into total real liters
    total_liters_flow = integrate.trapezoid(y=flow_rate_array, dx=1)

    return total_liters_flow, index_tracker


# Assuming carrier gas is saturated immediately, calculates grams of metal oxide contained
def liters_to_grams(liters, organometal):
    # gas constant in units "Torr" and "Liters"
    R_TORR_LITERS = 62.3638

    # calculates partial (Antoine Equation) pressure and applies (pv)/(rt) = n to get mols (factor of 2 added to account for tmal being dimer)
    # partial_pressure_torr = 10 ** (
    #     organometal.a - (organometal.b / (organometal.t + STANDARD_TEMPERATURE_KELVIN))
    # )
    mols = (organometal.partial_pressure_torr() * liters) / (
        R_TORR_LITERS * (organometal.t + STANDARD_TEMPERATURE_KELVIN)
    )
    grams = organometal.molar_mass * mols

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


class TMAl_Source:
    def __init__(self):
        self.name = "TMAl"
        self.bubbler_in_valve = "DO40"
        self.bubbler_out_valve = "DO38"
        self.blocking_valve = "DO39"
        self.mass_flow_controler = "AI32"
        self.pressure_flow_controler = "AI33"
        self.molar_mass = 72.09 * 2
        self.a = 8.224
        self.b = 2134.83
        self.t = -10

    def partial_pressure_torr(self):
        return 10 ** (self.a - (self.b / (self.t + STANDARD_TEMPERATURE_KELVIN)))

    def calculate_mass_and_time(self, file_path):
        df = pd.read_csv(file_path, delimiter=",", parse_dates=True, header=4)
        total_liters, index_tracker = slpm_to_liters(df, self)
        grams = float(liters_to_grams(total_liters, self))

        time = len(index_tracker)
        return time, grams


tmal = TMAl_Source()

# bubbler_in_valve = "DO40"
# bubbler_out_valve = "DO38"
# blocking_valve = "DO39"
# mass_flow_controler = "AI32"
# pressure_flow_controler = "AI33"
# molar_mass = 72.09 * 2
# a = 8.224
# b = 2134.83
# t = -10

test_amount = 0.009555694

# Selects all the files to be read
if PATH_VIA_TERMINAL:
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
else:
    file_path = r"C:/Users/gma78/Desktop/Excels/2024-06-28_S258_Datalog 6-28-2024 3-47-03 PM.csv"
    files = [file_path]

grams_by_run = []
time_by_run = []
dates_list = []
names_list = []

# Calculates the total time on and liters outputed of the given metal oxide/bubbler
for file in files:
    print(file)
    # dataframe = pd.read_csv(i, delimiter=",", parse_dates=True, header=4)
    # total_flow_liters, index_tracker = slpm_to_liters(dataframe)

    # total_grams = liters_to_grams(total_flow_liters)

    grams, time = tmal.calculate_mass_and_time(file)

    grams_by_run.append(grams)
    time_by_run.append(time)

    file_name = re.split("/|\\\\", file)
    designation = ((file_name)[-1].split(" "))[0]

    date = designation.split("_")[0]
    name = " ".join(designation.split("_")[1:])

    # file_name = ((designator)[-1].split(" "))[0]
    # file_date = ((designator)[-1].split(" "))[0]
    # TODO 1 split name into date and name
    names_list.append(name)
    dates_list.append(date)

grams_total = sum(grams_by_run)
time_total = sum(time_by_run)

by_run = pd.DataFrame(
    {
        "Date": dates_list,
        "Name": names_list,
        "Grams by run": grams_by_run,
        "Time by run": time_by_run,
    }
)

totals = pd.DataFrame({"Grams total": grams_total, "Time total": time_total}, index=[0])

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
