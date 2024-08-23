while(True):
    continue

data = df.loc[:, ["Date", "Time","DO38","DO39","DO40","AI32"]]

here = os.path.dirname(os.path.abspath(__file__))
json_directory = here + "\\" + "compound.json"
print("in")
print(json_directory)
print("out")