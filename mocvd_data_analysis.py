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
    pressure_array = np.squeeze(np.asarray(df.loc[index_tracker, [organometal.pressure_flow_controler]]))

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
            ((organometal.t + STANDARD_TEMPERATURE_KELVIN) / (STANDARD_TEMPERATURE_KELVIN))
            * (STANDARD_PRESSURE_TORR / (pressure_array[i] - organometal.partial_pressure_torr()))
        )

    # Numericaly integrates into total real liters
    total_liters_flow = integrate.trapezoid(y=flow_rate_array, dx=1)

    return total_liters_flow, index_tracker


# Assuming carrier gas is saturated immediately, calculates grams of metal oxide contained
def liters_to_grams(liters, organometal):
    # gas constant in units "Torr" and "Liters"
    R_TORR_LITERS = 62.3638

    # Applies (pv)/(rt) = n to get mols
    mols = (organometal.partial_pressure_torr() * liters) / (R_TORR_LITERS * (organometal.t + STANDARD_TEMPERATURE_KELVIN))
    grams = organometal.molar_mass * mols

    print(mols / 9.25)

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


class Organometal_Source:
    def __init__(
        self, name, bubbler_in_valve, bubbler_out_valve, blocking_valve, mass_flow_controler, pressure_flow_controler, molar_mass, a, b, t
    ):
        self.name = name
        self.bubbler_in_valve = bubbler_in_valve
        self.bubbler_out_valve = bubbler_out_valve
        self.blocking_valve = blocking_valve
        self.mass_flow_controler = mass_flow_controler
        self.pressure_flow_controler = pressure_flow_controler
        self.molar_mass = molar_mass
        self.a = a
        self.b = b
        self.t = t

    def partial_pressure_torr(self):
        return 10 ** (self.a - (self.b / (self.t + STANDARD_TEMPERATURE_KELVIN)))

    def calculate_mass_and_time(self, file_path):
        df = pd.read_csv(file_path, delimiter=",", parse_dates=True, header=4)
        total_liters, index_tracker = slpm_to_liters(df, self)

        grams = float(liters_to_grams(total_liters, self))
        time = len(index_tracker)

        return grams, time


tmal = Organometal_Source(
    name="TMAl",
    bubbler_in_valve="DO40",
    bubbler_out_valve="DO38",
    blocking_valve="DO39",
    mass_flow_controler="AI32",
    pressure_flow_controler="AI33",
    molar_mass=(72.09 * 2),
    a=8.224,
    b=2134.83,
    t=-10,
)

tmga = Organometal_Source(
    name="TMGa",
    bubbler_in_valve="DO28",
    bubbler_out_valve="DO26",
    blocking_valve="DO27",
    mass_flow_controler="AI38",
    pressure_flow_controler="todo",
    molar_mass=114.827,
    a=8.501,
    b=1824,
    t=-10,
)

PATH_VIA_TERMINAL = False

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

    grams, time = tmal.calculate_mass_and_time(file)

    file_name = re.split("/|\\\\", file)
    designation = ((file_name)[-1].split(" "))[0]
    date = designation.split("_")[0]
    name = " ".join(designation.split("_")[1:])

    grams_by_run.append(grams)
    time_by_run.append(time)
    names_list.append(name)
    dates_list.append(date)

grams_total = sum(grams_by_run)
time_total = sum(time_by_run)

by_run = pd.DataFrame(
    {
        "Date (yy/mm/dd)": dates_list,
        "Name": names_list,
        "Mass (Grams)": grams_by_run,
        "Time (Seconds)": time_by_run,
    }
)

totals = pd.DataFrame({"Total Mass (Grams)": grams_total, "Total Time (Seconds)": time_total}, index=[0])

result = pd.concat([by_run, totals], axis=1)

result.to_csv("file2.csv", index=False)

print("Result:\n", result)
print("Total grams of", tmal.name, ":", grams_total)
print("Total run time for", tmal.name, ":", time_total)
print("Finished")
