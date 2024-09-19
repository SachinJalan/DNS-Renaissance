# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# %%
"""
example csv file:
Domain,Total Packets,Total Bytes,Total DNS Packets,Total DNS Bytes,Total Time,Total DNS Time,TTFB
'domain.',4,264,4,264,0.0781857967376709,0.0781857967376709,9.989738464355469e-05
'2mdn.net.',4,272,4,272,0.4595179557800293,0.4595179557800293,9.012222290039062e-05
'3gppnetwork.org.',4,300,4,300,0.11552214622497559,0.11552214622497559,0.0001220703125
'3lift.com.',13,1823,4,524,0.11950492858886719,0.04582095146179199,8.20159912109375e-05
'a-msedge.net.',6,396,4,288,0.05035400390625,0.05025196075439453,8.392333984375e-05
"""

# %%
# df = pd.read_csv("results.csv")
df = pd.read_csv("data/results-200.csv")
df.head()


# %%
# clean up the data
# if total packets is 0 then remove the row
df = df[df["Total Packets"] != 0]
# if ttfb is 0 or -1 then remove the row
df = df[df["TTFB"] != 0]
df = df[df["TTFB"] != -1]
df.head()


# %%
# total packets vs total dns packets for

sns.scatterplot(data=df, x="Total Packets", y="Total DNS Packets")
plt.show()


# %%
# total bytes vs total dns bytes

sns.scatterplot(data=df, x="Total Bytes", y="Total DNS Bytes")
plt.show()


# %%
# total time vs total dns time

sns.scatterplot(data=df, x="Total Time", y="Total DNS Time")
plt.show()


# %%
# total time vs total dns time ratio
df["Total DNS Time Ratio"] = df["Total DNS Time"] / df["Total Time"]
sns.histplot(data=df, x="Total DNS Time Ratio")
plt.show()


# %%
# df headers: ['Domain', 'Total Packets', 'Total Bytes', 'Total DNS Packets',
# 'Total DNS Bytes', 'Total Time', 'Total DNS Time', 'TTFB',
# 'Total DNS Cycles-core', 'Total DNS Cycles-atom',
# 'Total DNS Energy-pkg', 'Total DNS Energy-psys', 'Visited Domains',
# 'Total DNS Time Ratio']

# %%
# number of visited domains vs total dns time ratio
df["Number of Visited Domains"] = df["Visited Domains"].apply(
    lambda x: len(x.split(","))
)
sns.scatterplot(data=df, x="Number of Visited Domains", y="Total DNS Time Ratio")
plt.show()

# %%
# number of visited domains vs total dns time
sns.scatterplot(data=df, x="Number of Visited Domains", y="Total DNS Time")
plt.show()

# %%
# number of visited domains histogram
sns.histplot(data=df, x="Number of Visited Domains")
plt.show()
