import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# 1) Import and inspect
raw = pd.read_csv("marketing_campaign_raw.csv")
print(raw.shape)
print(raw.head())
print(raw.info())
print(raw.isna().sum())
print("Exact duplicates:", raw.duplicated().sum())

# 2) NumPy: median and percentile
spend = pd.to_numeric(raw["Spend_EGP"],errors="coerce").dropna().to_numpy()
print("Median spend:", np.median(spend))
print("95th percentile spend:", np.percentile(spend,95))

# 3) Clean and validate
df = raw.copy()
df["Date"] = pd.to_datetime(df["Date"],errors="coerce")
df = df.drop_duplicates()
for col in ["Budget_EGP","Spend_EGP","Impressions","Clicks","Conversions","Revenue_EGP"]:
    df[col] = pd.to_numeric(df[col],errors="coerce")
for col in ["Budget_EGP","Spend_EGP","Impressions","Clicks","Conversions","Revenue_EGP"]:
    df.loc[df[col] < 0,col] = np.nan
df["Channel"] = df["Channel"].fillna("Unknown")
df["Audience"] = df["Audience"].fillna("Unknown")
df["Spend_EGP"] = df["Spend_EGP"].fillna(df["Spend_EGP"].median())
df["Impressions"] = df["Impressions"].fillna(df["Impressions"].median())
df["Clicks"] = df["Clicks"].fillna(0)
df["Conversions"] = df["Conversions"].fillna(0)
df["Revenue_EGP"] = df["Revenue_EGP"].fillna(0)
df["CTR"] = np.where(df["Impressions"]>0,df["Clicks"]/df["Impressions"],np.nan)
df["Conversion_Rate"] = np.where(df["Clicks"]>0,df["Conversions"]/df["Clicks"],np.nan)
df["CPC_EGP"] = np.where(df["Clicks"]>0,df["Spend_EGP"]/df["Clicks"],np.nan)
df["CPA_EGP"] = np.where(df["Conversions"]>0,df["Spend_EGP"]/df["Conversions"],np.nan)
df["ROAS"] = np.where(df["Spend_EGP"]>0,df["Revenue_EGP"]/df["Spend_EGP"],np.nan)
df["Month"] = df["Date"].dt.to_period("M").astype(str)

# 4) Aggregate analysis: use ratios of totals for correct weighted metrics
summary = df.groupby("Channel").agg(
    Spend=("Spend_EGP","sum"), Revenue=("Revenue_EGP","sum"),
    Impressions=("Impressions","sum"), Clicks=("Clicks","sum"),
    Conversions=("Conversions","sum")
)
summary["CTR"] = summary["Clicks"]/summary["Impressions"]
summary["CVR"] = summary["Conversions"]/summary["Clicks"]
summary["CPA_EGP"] = summary["Spend"]/summary["Conversions"].replace(0,np.nan)
summary["ROAS"] = summary["Revenue"]/summary["Spend"]
print(summary.round(3))

# 5) Matplotlib
summary["ROAS"].sort_values().plot(kind="barh",title="ROAS by channel")
plt.xlabel("Revenue / ad spend")
plt.tight_layout()
plt.show()

# 6) Seaborn
sns.boxplot(data=df,x="Campaign_Type",y="Spend_EGP")
plt.xticks(rotation=20)
plt.title("Spend distribution by campaign type")
plt.tight_layout()
plt.show()

# 7) Plotly
fig = px.scatter(df,x="CTR",y="Conversion_Rate",color="Channel",
                 size="Spend_EGP",hover_data=["Campaign_ID","Campaign_Type"],
                 title="CTR vs conversion rate")
fig.show()
