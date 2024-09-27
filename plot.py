# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# %%
"""
example csv file:
Domain,Total Packets,Total Bytes,Total DNS Packets,Total DNS Bytes,Total Time,Total DNS Time,TTFB,Total DNS Cycles-core,Total DNS Cycles-atom,Total DNS Energy-pkg,Total DNS Energy-psys,Visited Domains
iitgn.ac.in,2456,11577920,76,9414,67814.94188,2493.945122,583.4434032,177504750,177504750,9.35,22.44,"[""'iitgn.ac.in.'"", ""'www.googletagmanager.com.'"", ""'cdnjs.cloudflare.com.'"", ""'fonts.googleapis.com.'"", ""'cdn.usefathom.com.'"", ""'d1m1uiy1540nk9.cloudfront.net.'"", ""'www.facebook.com.'"", ""'px.ads.linkedin.com.'"", ""'fonts.gstatic.com.'""]"
"""

# %%
# df = pd.read_csv("results.csv")
df = pd.read_csv("data/results-1000.csv")
df.head()


# %%
# clean up the data
print(df.shape)
# if total packets is 0 then remove the row
df = df[df["Total Packets"] != 0]
# if ttfb is 0 or -1 then remove the row
df = df[df["TTFB"] != 0]
df = df[df["TTFB"] != -1]
df.head()
print(df.shape)


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

# %%

# cumulative distribution of total dns time ratio
sns.ecdfplot(data=df, x="Total DNS Time Ratio")
plt.show()

# %%
sns.histplot(data=df, y="Number of Visited Domains")
plt.show()


# %%
# bytes ratio
df["Bytes Ratio"] = df["Total DNS Bytes"] / df["Total Bytes"]
sns.histplot(data=df, x="Bytes Ratio")
plt.show()

# %%
# bytes ratio cdf
sns.ecdfplot(data=df, x="Bytes Ratio")
plt.show()


# %%
# energy vs dns-ratio
# sns.scatterplot(data=df, x="Total DNS Energy-pkg", y="Total DNS Time Ratio")
# sns.jointplot(data=df, x="Total DNS Energy-pkg", y="Total DNS Time Ratio", kind="hex")
# sns.displot(data=df, x="Total DNS Energy-pkg", y="Total DNS Time Ratio", kind="kde")
# sns.histplot(data=df, x="Total DNS Energy-pkg", y="Total DNS Time Ratio", bins=20, cbar=True)
# sns.pairplot(data=df, vars=["Total DNS Energy-pkg", "Total DNS Time Ratio"])
# sns.jointplot(data=df, x="Total DNS Energy-pkg", y="Total DNS Time Ratio", kind="kde")
# sns.kdeplot(data=df, x="Total DNS Energy-pkg", y="Total DNS Time Ratio", fill=True)
# sns.relplot(data=df, x="Total DNS Energy-pkg", y="Total DNS Time Ratio", hue="Number of Visited Domains")
# sns.clustermap(data=df[["Total DNS Energy-pkg", "Total DNS Time Ratio", "Number of Visited Domains"]])
sns.kdeplot(data=df, x="Total DNS Energy-pkg", y="Total DNS Time Ratio", fill=True)
sns.scatterplot(data=df, x="Total DNS Energy-pkg", y="Total DNS Time Ratio")
sns.rugplot(data=df, x="Total DNS Energy-pkg", y="Total DNS Time Ratio")
plt.show()


# %%
sns.relplot(
    data=df,
    x="Total DNS Energy-pkg",
    y="Total DNS Time Ratio",
    hue="Number of Visited Domains",
)
plt.show()

# %%
# print the correlation matrix and ignore the domain column, visited domains column
df_corr = df.drop(columns=["Domain", "Visited Domains"]).corr()
df_corr

sns.heatmap(df_corr)
plt.show()

# %%
# print some statistics
df_stats = df.describe()
df_stats

# %%
# boxplot
sns.boxplot(data=df, log_scale=True, orient="h")
plt.show()

# %%
# pairplot
# sns.pairplot(data=df)
# plt.show()

# %%
sns.ecdfplot(data=df, log_scale=True)
plt.show()

# %%
# normalizing the data
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
df_norm = df.copy().drop(columns=["Visited Domains"])
df_norm[df_norm.columns[1:]] = scaler.fit_transform(df_norm[df_norm.columns[1:]])
df_norm.head()

# %%
# boxplot
sns.boxplot(data=df_norm, orient="h", log_scale=True)
plt.show()

# %%
sns.ecdfplot(data=df_norm)
plt.show()

# %%
# pdf plot
sns.kdeplot(data=df_norm)
plt.show()

# %%
df_norm.describe()


# %%
df_2 = pd.read_csv("results-test-2.csv")
df_2.head()

# %%
# clean up the data
print(df_2.shape)
df_2 = df_2[df_2["Total Packets"] != 0]
df_2 = df_2[df_2["TTFB"] != 0]
df_2 = df_2[df_2["TTFB"] != -1]
df_2.head()
print(df_2.shape)

# %%
# few lines of csv file
# Domain,Total Packets,Total Bytes,Total DNS Packets,Total DNS Bytes,Total Time,Total DNS Time,TTFB,Total DNS Cycles-core,Total DNS Cycles-atom,Total DNS Energy-pkg,Total DNS Energy-psys,Total DNS Energy-cores,Visited Domains
# adobe.com,53,13346,10,1864,3379.168748855591,401.42822265625,500.652551651001,79191879,7815510,3.58,6.78,1.77,"{""'adobe.com.'"": {'Total Packets': 6, 'Total Response Packets': 4, 'Total Query Packets': 2, 'qtypes': ['A', 'AAAA'], 'qclasses': ['IN', 'IN'], 'rtypes': ['AAAA', 'AAAA', 'AAAA', 'AAAA', 'A', 'A', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'A', 'A'], 'rclasses': ['IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN']}, ""'www.adobe.com.'"": {'Total Packets': 4, 'Total Response Packets': 2, 'Total Query Packets': 2, 'qtypes': ['A', 'AAAA'], 'qclasses': ['IN', 'IN'], 'rtypes': ['CNAME', 'CNAME', 'CNAME', 'A', 'A', 'CNAME', 'CNAME', 'CNAME', 'AAAA', 'AAAA', 'AAAA', 'AAAA'], 'rclasses': ['IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN']}}"
# adobe.io,13,1141,2,376,782.2246551513672,0.1366138458251953,186.86461448669434,-1,0,0,0,0,"{""'adobe.io.'"": {'Total Packets': 2, 'Total Response Packets': 2, 'Total Query Packets': 0, 'qtypes': [], 'qclasses': [], 'rtypes': ['A', 'A', 'A', 'A', 'AAAA', 'AAAA', 'AAAA', 'AAAA'], 'rclasses': ['IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN']}}"
# adsafeprotected.com,7,1062,2,634,6.3495635986328125,0.9930133819580078,-1,-1,0,0,0,0,"{""'adsafeprotected.com.'"": {'Total Packets': 2, 'Total Response Packets': 2, 'Total Query Packets': 0, 'qtypes': [], 'qclasses': [], 'rtypes': ['AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'A', 'A', 'A', 'A'], 'rclasses': ['IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN']}}"
# adsrvr.org,563,1149401,58,10926,15701.669692993164,755.842924118042,697.5834369659424,555464426,33415024,30.280000000000005,65.74000000000001,7.779999999999996,"{""'adsrvr.org.'"": {'Total Packets': 18, 'Total Response Packets': 10, 'Total Query Packets': 8, 'qtypes': ['A', 'AAAA', 'A', 'AAAA', 'A', 'AAAA', 'A', 'AAAA'], 'qclasses': ['IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN'], 'rtypes': ['A', 'A', 'A', 'A', 'A', 'A', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'A', 'A', 'A', 'A', 'A', 'A', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'A', 'A', 'A', 'A', 'A', 'A'], 'rclasses': ['IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN']}, ""'www.thetradedesk.com.'"": {'Total Packets': 24, 'Total Response Packets': 12, 'Total Query Packets': 12, 'qtypes': ['A', 'AAAA', 'A', 'AAAA', 'A', 'AAAA', 'A', 'AAAA', 'A', 'AAAA', 'A', 'AAAA'], 'qclasses': ['IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN'], 'rtypes': ['CNAME', 'A', 'A', 'A', 'CNAME', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'CNAME', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'CNAME', 'A', 'A', 'A', 'CNAME', 'A', 'A', 'A', 'CNAME', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'CNAME', 'A', 'A', 'A', 'CNAME', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'CNAME', 'A', 'A', 'A', 'CNAME', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'CNAME', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'CNAME', 'A', 'A', 'A'], 'rclasses': ['IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN']}, ""'thetradedesk.com.'"": {'Total Packets': 16, 'Total Response Packets': 8, 'Total Query Packets': 8, 'qtypes': ['A', 'AAAA', 'A', 'AAAA', 'A', 'AAAA', 'A', 'AAAA'], 'qclasses': ['IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN'], 'rtypes': ['A', 'A', 'A', 'A', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'A', 'A', 'A', 'A', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA', 'AAAA'], 'rclasses': ['IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN', 'IN']}}"

# note that the visited domains are in python dictionary format
# it now contains the total packets, total response packets, total query packets, qtypes, qclasses, rtypes, rclasses


# %%
# dns time ratio
df_2["Total DNS Time Ratio"] = df_2["Total DNS Time"] / df_2["Total Time"]
sns.histplot(data=df_2, x="Total DNS Time Ratio")
plt.show()

# %%
# number of dns resolutions, qtypes, rtypes, qclasses, rclasses, number of visited domains
df_2["Number of Visited Domains"] = df_2["Visited Domains"].apply(
    lambda x: len(x.split(","))
)
visited_domains_dict = df_2["Visited Domains"].apply(eval)
df_2["Number of DNS Resolutions"] = visited_domains_dict.apply(
    lambda x: sum([x[key]["Total Packets"] for key in x])
)
df_2["Number of DNS Queries"] = visited_domains_dict.apply(
    lambda x: sum([x[key]["Total Query Packets"] for key in x])
)
df_2["Number of DNS Responses"] = visited_domains_dict.apply(
    lambda x: sum([x[key]["Total Response Packets"] for key in x])
)

# %%
df_2.head()

# %%
df_2.describe()

# %%
sns.ecdfplot(data=df_2, x="Number of DNS Resolutions")
plt.show()

# %%
sns.ecdfplot(data=df_2, x="Total DNS Packets")
plt.show()

# %%
sns.ecdfplot(data=df_2, x="Number of DNS Queries")
sns.ecdfplot(data=df_2, x="Number of DNS Responses")
plt.show()

# %%
sns.histplot(data=df_2, x="Number of DNS Queries")
plt.show()

# %%
# array of qtypes, rtypes, qclasses, rclasses
df_2["QTypes"] = visited_domains_dict.apply(
    lambda x: [item for sublist in [x[k]["qtypes"] for k in x] for item in sublist]
)
df_2["RTypes"] = visited_domains_dict.apply(
    lambda x: [item for sublist in [x[k]["rtypes"] for k in x] for item in sublist]
)
df_2["QClasses"] = visited_domains_dict.apply(
    lambda x: [item for sublist in [x[k]["qclasses"] for k in x] for item in sublist]
)
df_2["RClasses"] = visited_domains_dict.apply(
    lambda x: [item for sublist in [x[k]["rclasses"] for k in x] for item in sublist]
)
df_2.head()


# %%
# qtypes, rtypes, qclasses, rclasses dictionary column
df_2["QTypesDict"] = df_2["QTypes"].apply(
    lambda x: {item: x.count(item) for item in set(x)}
)
df_2["RTypesDict"] = df_2["RTypes"].apply(
    lambda x: {item: x.count(item) for item in set(x)}
)
df_2["QClassesDict"] = df_2["QClasses"].apply(
    lambda x: {item: x.count(item) for item in set(x)}
)
df_2["RClassesDict"] = df_2["RClasses"].apply(
    lambda x: {item: x.count(item) for item in set(x)}
)
df_2.head()


# %%
qtypes_expanded = pd.DataFrame(df_2["QTypesDict"].tolist())
rtypes_expanded = pd.DataFrame(df_2["RTypesDict"].tolist())
qclasses_expanded = pd.DataFrame(df_2["QClassesDict"].tolist())
rclasses_expanded = pd.DataFrame(df_2["RClassesDict"].tolist())
df_2_expanded = pd.concat(
    # [df_2, qtypes_expanded, rtypes_expanded, qclasses_expanded, rclasses_expanded],
    [qtypes_expanded, rtypes_expanded, qclasses_expanded, rclasses_expanded],
    axis=1,
)
df_2_expanded.head()

# %%
sns.boxenplot(data=df_2_expanded, orient="h", showfliers=False)
plt.show()
sns.boxplot(data=df_2_expanded, orient="h", showfliers=False)
plt.show()

# %%
# histogram of byte ratio, dns time ratio, dns packet ratio
df_2["Total Bytes Ratio"] = df_2["Total DNS Bytes"] / df_2["Total Bytes"]
df_2["Total DNS Time Ratio"] = df_2["Total DNS Time"] / df_2["Total Time"]
df_2["Total DNS Packet Ratio"] = df_2["Total DNS Packets"] / df_2["Total Packets"]


# %%
sns.histplot(data=df_2, x="Total Bytes Ratio")
plt.show()

# %%
sns.histplot(data=df_2, x="Total DNS Time Ratio")
plt.show()

# %%
sns.histplot(data=df_2, x="Total DNS Packet Ratio")
plt.show()

# %%
sns.ecdfplot(data=df_2, x="Total Bytes Ratio")
sns.ecdfplot(data=df_2, x="Total DNS Time Ratio")
sns.ecdfplot(data=df_2, x="Total DNS Packet Ratio")
plt.axvline(0.05, color="red", linestyle="--")
plt.xlabel("Ratio")
plt.legend(["Bytes", "Time", "Packets"])
plt.grid()
plt.show()

# %%
