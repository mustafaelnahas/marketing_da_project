import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(page_title="Marketing Campaign Analysis", layout="wide")
st.title("Marketing Campaign Analysis")
st.caption("Challenge-based graduation project • Synthetic campaign data • EGP")

@st.cache_data
def load_data():
    return pd.read_csv("marketing_campaign_raw.csv")

raw = load_data()
df = raw.copy()
rows_before = len(df)
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.drop_duplicates()

num_cols = ["Budget_EGP","Spend_EGP","Impressions","Clicks","Conversions","Revenue_EGP"]
for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df.loc[df["Budget_EGP"] < 0, "Budget_EGP"] = np.nan
df.loc[df["Spend_EGP"] < 0, "Spend_EGP"] = np.nan
df.loc[df["Impressions"] < 0, "Impressions"] = np.nan
df.loc[df["Clicks"] < 0, "Clicks"] = np.nan
df.loc[df["Conversions"] < 0, "Conversions"] = np.nan
df.loc[df["Revenue_EGP"] < 0, "Revenue_EGP"] = np.nan
df["Channel"] = df["Channel"].fillna("Unknown")
df["Campaign_Type"] = df["Campaign_Type"].fillna("Unknown")
df["Audience"] = df["Audience"].fillna("Unknown")
df["Spend_EGP"] = df["Spend_EGP"].fillna(df["Spend_EGP"].median())
df["Impressions"] = df["Impressions"].fillna(df["Impressions"].median())
df["Clicks"] = df["Clicks"].fillna(0)
df["Conversions"] = df["Conversions"].fillna(0)
df["Revenue_EGP"] = df["Revenue_EGP"].fillna(0)
# Flag/cap extreme spend for classroom demonstration; in real work investigate source records first
spend_cap = df["Spend_EGP"].quantile(.99)
df["Spend_EGP"] = df["Spend_EGP"].clip(upper=spend_cap)
df["CTR"] = np.where(df["Impressions"] > 0, df["Clicks"] / df["Impressions"], np.nan)
df["Conversion_Rate"] = np.where(df["Clicks"] > 0, df["Conversions"] / df["Clicks"], np.nan)
df["CPC_EGP"] = np.where(df["Clicks"] > 0, df["Spend_EGP"] / df["Clicks"], np.nan)
df["CPA_EGP"] = np.where(df["Conversions"] > 0, df["Spend_EGP"] / df["Conversions"], np.nan)
df["ROAS"] = np.where(df["Spend_EGP"] > 0, df["Revenue_EGP"] / df["Spend_EGP"], np.nan)
df["Profit_After_Ad_Spend_EGP"] = df["Revenue_EGP"] - df["Spend_EGP"]
df["Month"] = df["Date"].dt.to_period("M").astype(str)

st.sidebar.header("Filters")
channels = ["All"] + sorted(df["Channel"].dropna().unique().tolist())
channel = st.sidebar.selectbox("Channel", channels)
types = ["All"] + sorted(df["Campaign_Type"].dropna().unique().tolist())
ctype = st.sidebar.selectbox("Campaign type", types)
regions = ["All"] + sorted(df["Region"].dropna().unique().tolist())
region = st.sidebar.selectbox("Region", regions)
audiences = ["All"] + sorted(df["Audience"].dropna().unique().tolist())
audience = st.sidebar.selectbox("Audience", audiences)

f = df.copy()
if channel != "All": f = f[f["Channel"] == channel]
if ctype != "All": f = f[f["Campaign_Type"] == ctype]
if region != "All": f = f[f["Region"] == region]
if audience != "All": f = f[f["Audience"] == audience]

total_spend = f["Spend_EGP"].sum()
total_revenue = f["Revenue_EGP"].sum()
total_conversions = f["Conversions"].sum()
ctr = f["Clicks"].sum()/f["Impressions"].sum() if f["Impressions"].sum() else 0
cvr = f["Conversions"].sum()/f["Clicks"].sum() if f["Clicks"].sum() else 0
roas = total_revenue/total_spend if total_spend else 0
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Ad spend", f"{total_spend:,.0f} EGP")
c2.metric("Revenue", f"{total_revenue:,.0f} EGP")
c3.metric("Conversions", f"{total_conversions:,.0f}")
c4.metric("CTR", f"{ctr*100:.2f}%")
c5.metric("ROAS", f"{roas:.2f}x")

st.subheader("Channel performance")
left,right = st.columns(2)
with left:
    channel_perf = f.groupby("Channel",as_index=False).agg(
        Spend=("Spend_EGP","sum"), Revenue=("Revenue_EGP","sum"),
        Clicks=("Clicks","sum"), Conversions=("Conversions","sum"))
    channel_perf["ROAS"] = np.where(channel_perf["Spend"]>0,channel_perf["Revenue"]/channel_perf["Spend"],np.nan)
    fig = px.bar(channel_perf,x="Channel",y="ROAS",color="Channel",title="ROAS by channel")
    st.plotly_chart(fig,use_container_width=True)
with right:
    monthly = f.groupby("Month",as_index=False).agg(Spend=("Spend_EGP","sum"),Revenue=("Revenue_EGP","sum"))
    fig = px.line(monthly,x="Month",y=["Spend","Revenue"],markers=True,title="Monthly spend vs revenue")
    st.plotly_chart(fig,use_container_width=True)

st.subheader("Funnel and efficiency")
left,right = st.columns(2)
with left:
    f["CTR_Pct"] = f["CTR"]*100
    f["CVR_Pct"] = f["Conversion_Rate"]*100
    fig = px.scatter(f,x="CTR_Pct",y="CVR_Pct",color="Channel",size="Spend_EGP",
                     hover_data=["Campaign_ID","Campaign_Type","Spend_EGP","Conversions"],
                     title="Campaign CTR vs conversion rate")
    st.plotly_chart(fig,use_container_width=True)
with right:
    audience_perf = f.groupby("Audience",as_index=False).agg(
        Spend=("Spend_EGP","sum"),Conversions=("Conversions","sum"),Revenue=("Revenue_EGP","sum"))
    audience_perf["CPA"] = np.where(audience_perf["Conversions"]>0,audience_perf["Spend"]/audience_perf["Conversions"],np.nan)
    fig = px.bar(audience_perf,x="Audience",y="CPA",color="Audience",title="Cost per acquisition by audience")
    st.plotly_chart(fig,use_container_width=True)

with st.expander("Data quality checks"):
    st.write(f"Rows before removing duplicates: {rows_before:,}")
    st.write(f"Rows after removing duplicates: {len(df):,}")
    st.dataframe(df.isna().sum().rename("Missing values").to_frame())
    st.caption("Teaching note: metric denominators matter. Aggregate CTR = total clicks / total impressions; aggregate ROAS = total revenue / total ad spend. Do not average row-level ratios without considering weights.")

with st.expander("Explore filtered campaign records"):
    st.dataframe(f,use_container_width=True)
    st.download_button("Download filtered data",f.to_csv(index=False).encode("utf-8"),
                       file_name="filtered_marketing_campaigns.csv",mime="text/csv")

st.subheader("Suggested marketing actions")
st.markdown("""
- Reallocate budget only after comparing ROAS, conversion volume, CPA, and campaign objective.
- Separate awareness campaigns from conversion campaigns; they should not be judged by the same KPI.
- Investigate high-CTR / low-conversion campaigns for landing-page, audience, or offer mismatch.
- Check extreme spend and conversion values against the advertising platform before changing records.
- Use a controlled A/B test to validate changes instead of treating correlation as causation.
""")
