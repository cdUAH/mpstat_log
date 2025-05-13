import pandas as pd
import matplotlib.pyplot as plt

# mpstat_df.2.1.py
# 5/13/2025

columns = ['Epoch', 'CPU#', 'User%', 'Sys%', 'Idle%', 'MB_Used', 'MB_Free']
###########################################################################
filename = input("Enter your filename (mpstat_log_xzy.log) here: ")
granularity = input("If you need to adjust granularity, enter a value here (200-800 recommended, press enter for default of 500): ")
if granularity == "":
    granularity = 500
else:
    granularity = int(granularity)

xaxis_clutter = input("If the x-axis is too clutered with labels, enter 10 here. If it is still to cluttered, enter 8. If no changes needed, press 'enter': ")
if xaxis_clutter == "":
    xaxis_clutter = 12
    xaxis_clutter_major = 12
    xaxis_clutter_minor = 24
else:
    xaxis_clutter_major = int(xaxis_clutter)
    xaxis_clutter_minor = xaxis_clutter_major * 2


###########################################################################
print("\n")
print('--' * 25)
print(f"Running analysis on {filename} with the following parameters:\n"
      f"granularity = {granularity}\n"
      f"x-axis major ticks = {xaxis_clutter_major}\n"
      f"x-axis minor ticks = {xaxis_clutter_minor}")
print('--' * 25)
print("\n")
df1 = pd.read_csv(filename, sep=r"\s+", header=None, skiprows=3, on_bad_lines="skip")
print(df1)
df1 = df1.drop(columns=[1, 2, 3, 4, 5, 8, 10, 11, 12, 13, 14, 15, 17, 19, 20, 22, 23])
df1.columns = columns

customrange = input("If you want a custom time range, enter 'y'; for full file analysis, press 'enter': ")
if customrange.lower() == "y":  # Prompts user for start/end inputs in epoch
    start_range = int(input("Start (Epoch value): "))
    end_range = int(input("End (Epoch value): "))
    
    df1_f = df1[(df1["Epoch"] >= start_range) & (df1["Epoch"] <= end_range)]
    df1 = df1_f

print(df1)
df1 = df1[pd.to_numeric(df1["CPU#"], errors="coerce").notnull()]  # coerces any non-numeric values to get skipped, need
# for the next line (below) or else any mid-dataset labeled columns will throw error
df1['CPU#'] = df1['CPU#'].astype(float)
#df1 = df1[df1['CPU#'] <= 129]  # Patch fix. The code reads the shifted values from bad lines as RAM values. For my
# use case, this works. However, there could be issues with this in the future. What I need to do is set it up, so it
# will drop these bad rows all together. Maybe based on size?
# EDIT: it is fixed below, but I'll keep the above code in just as a backup
df1 = df1.dropna()
print(f"dataframe after dropping NANs: {df1}")
df1['Idle%'] = df1['Idle%'].astype(float)
df1["Datetime"] = pd.to_datetime(df1["Epoch"], unit="s")
df1["Datetime"] = df1["Datetime"].dt.strftime("%m-%d %H:%M GMT")  # Create datetime string

#####################################################
# EDIT DENOMINATOR BELOW FOR GRANULARITY. I would suggest 200-800. This is also set as a user-input
rolling_window = max(1, len(df1) // granularity)
print(rolling_window)
#####################################################

df1["Trend_Idle%"] = df1.groupby("CPU#")["Idle%"].transform(
    lambda x: x.rolling(window=rolling_window, min_periods=1).mean())

df1["Spike_count"] = df1.groupby("CPU#")["Idle%"].transform(
    lambda x: x.rolling(window=rolling_window, min_periods=1).apply(lambda y: (y <= .5).sum(), raw=True))



fig, ax1 = plt.subplots(figsize=(14, 7))

############### EDIT BELOW IF NEEDED #################
ax1.xaxis.set_major_locator(plt.MaxNLocator(xaxis_clutter_major))  # Set this to be 1/2 of below line
ax1.xaxis.set_minor_locator(plt.MaxNLocator(xaxis_clutter_minor)) 
#####################################################

for cpu in df1["CPU#"].unique():
    cpu_data = df1[df1["CPU#"] == cpu]

    # Plot rolling average trend line
    ax1.plot(cpu_data["Datetime"], cpu_data["Trend_Idle%"], label=f"CPU {cpu} Trend", alpha=0.7)

    # Plot 0% Idle spike counts (dashed line)
    ax1.plot(cpu_data["Datetime"], cpu_data["Spike_count"], linestyle="dashed", label=f"CPU {cpu} 0% Count",
             alpha=0.7)
# ax1.set_xticks(df1["Epoch"])
# ax1.set_xticklabels(df1["Datetime"])
ax1.set_xlabel("Date, Time")
ax1.set_ylabel("CPU Idle% (Top) & Spikes (Bottom)")
ax1.legend(loc="upper left")

# --------------------------------------------------------------
# Uncomment Below to enable RAM tracking
# Right Y-Axis (Memory Usage)

#df1["Avg_RAM_used"] = df1.groupby("Datetime")["MB_Used"].transform("mean")
#df1["Idle%Spikes"] = (df1["Idle%Spikes"] / rolling_window) * 100
#ax2 = ax1.twinx()
#ax2.plot(df1["Datetime"], df1["Avg_RAM_used"], color="grey", label="Avg_RAM_used", alpha=0.6)
#ax2.plot(df1["Datetime"], df1["Spike_count"], color="grey", label="Avg_RAM_used", alpha=0.6)
#ax2.set_ylabel("RAM (MB)")
#ax2.set_ylim(1500, 7200)
#ax2.legend(loc="upper right")
# --------------------------------------------------------------

fig.suptitle("CPU Trends, Spike_count, and Memory Usage")
plt.grid(alpha= 0.5, which = 'minor')
plt.grid(alpha= 0.25, which = 'major')
plt.show()
input("Press enter to end")
