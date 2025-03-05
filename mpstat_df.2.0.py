import pandas as pd
import matplotlib.pyplot as plt

columns = ['Epoch', 'CPU#', 'User%', 'Sys%', 'Idle%', 'MB_Used', 'MB_Free']
df1 = pd.read_csv('60h_mpstat_log_03032025.log', sep=r"\s+", header=None).iloc[1:]  # filename here
df1 = df1.drop(columns=[1, 2, 3, 4, 5, 8, 10, 11, 12, 13, 14, 15, 17, 19, 20, 22, 23])
df1.columns = columns
print(df1.head(10))
print(df1.dtypes)
df1['CPU#'] = df1['CPU#'].astype(float)
df1['Idle%'] = df1['Idle%'].astype(float)

print(df1.dtypes)

rolling_window = max(1, len(df1) // 100)

df1["Trend_Idle%"] = df1.groupby("CPU#")["Idle%"].transform(
    lambda x: x.rolling(window=rolling_window, min_periods=1).mean())

df1["Spike_count"] = df1.groupby("CPU#")["Idle%"].transform(
    lambda x: x.rolling(window=rolling_window, min_periods=1).apply(lambda y: (y == 0).sum(), raw=True))

df1["Avg_RAM_used"] = df1.groupby("Epoch")["MB_Used"].transform("mean")

fig, ax1 = plt.subplots(figsize=(12, 6))
for cpu in df1["CPU#"].unique():
    cpu_data = df1[df1["CPU#"] == cpu]

    # Plot rolling average trend line
    ax1.plot(cpu_data["Epoch"], cpu_data["Trend_Idle%"], label=f"CPU {cpu} Trend", alpha=0.7)

    # Plot 0% Idle spike counts (dashed line)
    ax1.plot(cpu_data["Epoch"], cpu_data["Spike_count"], linestyle="dashed", label=f"CPU {cpu} 0% Count",
             alpha=0.7)

ax1.set_xlabel("Epoch Time")
ax1.set_ylabel("CPU Idle% (Top) & Spikes (Bottom)")
ax1.legend(loc="upper left")

# Right Y-Axis (Memory Usage)
ax2 = ax1.twinx()
ax2.plot(df1["Epoch"], df1["Avg_RAM_used"], color="grey", label="Avg_RAM_used", alpha=0.6)
ax2.set_ylabel("RAM (MB)")
ax2.set_ylim(1500, 7200)

fig.suptitle("CPU Trends, Spike_count, and Memory Usage")
ax2.legend(loc="upper right")

plt.show()
