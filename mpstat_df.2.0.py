import pandas as pd
import matplotlib.pyplot as plt

columns = ['Epoch', 'CPU#', 'User%', 'Sys%', 'Idle%', 'MB_Used', 'MB_Free']
filename = 'logfilenamehere.log'  # Enter your (already modified) log file. See README

df1 = pd.read_csv(filename, sep=r"\s+", header=None)
df1 = df1.drop(columns=[1, 2, 3, 4, 5, 8, 10, 11, 12, 13, 14, 15, 17, 19, 20, 22, 23])
df1.columns = columns

customrange = input("y for custom, n for code-based, or enter for full (epoch time required): ")
if customrange.lower() == "y":  # Prompts user for start/end inputs in epoch
    start_range = int(input("Start: "))
    end_range = int(input("End: "))
    
    df1_f = df1[(df1["Epoch"] >= start_range) & (df1["Epoch"] <= end_range)]
    df1 = df1_f

if customrange.lower() == "n":  # Manual option. Good for running the same time over and over
    start_range = 1742187600
    end_range = 1742392800
    df1_f = df1[(df1["Epoch"] >= start_range) & (df1["Epoch"] <= end_range)]
    df1 = df1_f


df1['CPU#'] = df1['CPU#'].astype(float)
df1['Idle%'] = df1['Idle%'].astype(float)
df1["Datetime"] = pd.to_datetime(df1["Epoch"], unit="s")
df1["Datetime"] = df1["Datetime"].dt.strftime("3-%d %H:%M GMT")  # Create datetime string
# print(df1["Datetime"])
# print(df1["Epoch"])
# print()


rolling_window = max(1, len(df1) // 500)  # Window. Adjust denominator for granularity. See README

df1["Trend_Idle%"] = df1.groupby("CPU#")["Idle%"].transform(
    lambda x: x.rolling(window=rolling_window, min_periods=1).mean())

df1["Spike_count"] = df1.groupby("CPU#")["Idle%"].transform(
    lambda x: x.rolling(window=rolling_window, min_periods=1).apply(lambda y: (y <= .5).sum(), raw=True))

#df1["Avg_RAM_used"] = df1.groupby("Datetime")["MB_Used"].transform("mean")

fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.xaxis.set_major_locator(plt.MaxNLocator(12))  # Set this to be 1/2 of below line
ax1.xaxis.set_minor_locator(plt.MaxNLocator(24)) 
for cpu in df1["CPU#"].unique():
    cpu_data = df1[df1["CPU#"] == cpu]

    # Plot rolling average trend line
    ax1.plot(cpu_data["Datetime"], cpu_data["Trend_Idle%"], label=f"CPU {cpu} Trend", alpha=0.7)

    # Plot 0% Idle spike counts (dashed line)
    ax1.plot(cpu_data["Datetime"], cpu_data["Spike_count"], linestyle="dashed", label=f"CPU {cpu} 0% Count",
             alpha=0.7)
    
ax1.set_xlabel("Date, Time")
ax1.set_ylabel("CPU Idle% (Top) & Spikes (Bottom)")
ax1.legend(loc="upper left")
# --------------------------------------------------------------
# Uncomment Below to enable RAM tracking
# Right Y-Axis (Memory Usage)

#df1["Idle%Spikes"] = (df1["Idle%Spikes"] / rolling_window) * 100
#ax2 = ax1.twinx()
#ax2.plot(df1["Datetime"], df1["Avg_RAM_used"], color="grey", label="Avg_RAM_used", alpha=0.6)
#ax2.plot(df1["Datetime"], df1["Spike_count"], color="grey", label="Avg_RAM_used", alpha=0.6)
#ax2.set_ylabel("RAM (MB)")
#ax2.set_ylim(1500, 7200)
#ax2.legend(loc="upper right")
# --------------------------------------------------------------
fig.suptitle("CPU Trends, Spike_count, and Memory Usage")
plt.show()
