import os
from tkinter import filedialog as fd
import numpy as np
import pandas as pd
from scipy import integrate

PATH_VIA_TERMINAL = True

VERY_BIG_NUMBER = 1_000_000

if PATH_VIA_TERMINAL == False:
    print("Enter folder location")
    file_path = fd.askopenfilename()
    print(file_path)
else:
    file_path = r"C:\Users\gma78\Desktop\2024-06-28_S258_Datalog 6-28-2024 3-47-03 PM.csv"

df = pd.read_csv(file_path, delimiter=',', parse_dates=True, header=4)

#data = df.loc[:, ["Date", "Time","DO38","DO39","DO40","AI32"]]

material = "AlN"

if material == "GaN":
    bubbler_in_valve = "DO28"
    bubbler_out_valve = "DO26"
    blocking_valve = "DO27"

if material == "AlN":
    bubbler_in_valve = "DO40"
    bubbler_out_valve = "DO38"
    blocking_valve = "DO39"

list = []
for i in range(len(df["Date"])):
    if df.loc[i, blocking_valve] == 0 and df.loc[i, bubbler_out_valve] == 1 and df.loc[i, bubbler_in_valve] == 1:
        list.append(i)
np_metal_outs = np.squeeze(np.asarray(df.loc[list, ["AI32"]]))
metal_outs = df.loc[list, ["AI32"]]

print(np_metal_outs)
print(type(np_metal_outs))

used_metal = integrate.trapezoid(y = np_metal_outs, dx = 1)

list_string = '\n'.join(str(x) for x in list)

print(metal_outs.head(VERY_BIG_NUMBER))

html = (df.style).to_html()
f = open("demofile.html", "w")
f.write(html)
f.close()

f = open("demofile2.txt", "w")
f.write(list_string)
f.close()

print("in")
print(used_metal)
print("out")
# df.head()
