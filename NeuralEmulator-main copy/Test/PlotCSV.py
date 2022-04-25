import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(r"C:\Users\Avi\Desktop\IntelliSpikesLab\Emulator\tuneCurves\curves.csv")
x = df["VIN"]
for col in df.columns:
    if col != "VIN":
        plt.plot(x,df[col])

plt.show()
