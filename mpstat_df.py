import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from scipy.signal import savgol_filter


columns = ['Epoch', 'CPU#', 'User%', 'Sys%', 'Idle%', 'MB_Used', 'MB_Free']
df1 = pd.read_csv('24h_mpstat_log_03032025.log', sep=r"\s+", header=None).iloc[1:]
df1 = df1.drop(columns=[1, 2, 3, 4, 5, 8, 10, 11, 12, 13, 14, 15, 17, 19, 20, 22, 23])
df1.columns = columns
print(df1.head(10))
print(df1.dtypes)
df1['CPU#'] = df1['CPU#'].astype(float)
df1['Idle%'] = df1['Idle%'].astype(float)
print(df1.dtypes)

#######
#df1["Smoothed_Idle%"] = df1['Idle%'] # default for raw values

#df1["Smoothed_Idle%"] = lowess(df1['Idle%'], df1['Epoch'], frac=0.005)[:,1] #lowess attempt, adjust frac
#df1["Smoothed_Idle%"] = gaussian_filter(df1["Idle%"], sigma=7) #gaussian attempt. Adjust sigma
#df1["Smoothed_Idle%"] = savgol_filter(df1['Idle%'], window_length=10, polyorder=8) #savitzky-golay. Adj wl or po


df1["Smoothed_Idle%"] = 0  # placeholder
for cpu in df1["CPU#"].unique():
    mask = df1["CPU#"] == cpu
    span = max(15, min(30, df1.loc[mask, "Idle%"].var() / 7))  # Adaptive span. Adjust max, min values for smoothness
    df1.loc[mask, "Smoothed_Idle%"] = df1.loc[mask, "Idle%"].ewm(span=span, adjust=False).mean()


#######




memory_avg = df1.groupby("Epoch")[["MB_Used", "MB_Free"]].mean()

cpu3 = df1[df1["CPU#"] == 3][["Epoch", "Smoothed_Idle%"]]
cpu18 = df1[df1["CPU#"] == 18][["Epoch", "Smoothed_Idle%"]]
cpu19 = df1[df1["CPU#"] == 19][["Epoch", "Smoothed_Idle%"]]


###############################################
# Plotting/Formatting with MatPlotLib ALL BELOW
###############################################
fig, ax1 = plt.subplots(figsize=(10, 5))

# ax1.plot(cpu3["Epoch"], cpu3["Smoothed_Idle%"], label="CPU 3 Idle%", marker="o", color="blue")
# ax1.plot(cpu18["Epoch"], cpu18["Smoothed_Idle%"], label="CPU 18 Idle%", marker="s", color="green")
# ax1.plot(cpu19["Epoch"], cpu19["Smoothed_Idle%"], label="CPU 19 Idle%", marker="^", color="red")

ax1.plot(cpu3["Epoch"], cpu3["Smoothed_Idle%"], label="CPU 3 Idle%", color="blue")
ax1.plot(cpu18["Epoch"], cpu18["Smoothed_Idle%"], label="CPU 18 Idle%", color="green")
ax1.plot(cpu19["Epoch"], cpu19["Smoothed_Idle%"], label="CPU 19 Idle%", color="red")

# Set left y-axis properties
ax1.set_xlabel("Epoch")
ax1.set_ylabel("Idle % (0%-100%)")
ax1.set_ylim(100, 0)
ax1.legend(loc="upper left")
ax1.grid(True, linestyle="--", alpha=0.5)

# Create a second y-axis for memory usage
ax2 = ax1.twinx()
ax2.plot(memory_avg.index, memory_avg["MB_Used"], label="Avg MB Used", linestyle="--", color="purple")

# Set right y-axis properties
ax2.set_ylabel("Memory Used (MB)")
ax2.set_ylim(6000, 7500)
ax2.legend(loc="upper right")

# Show the plot
plt.title("CPU Idle% and Memory Usage Over Time")
plt.show()