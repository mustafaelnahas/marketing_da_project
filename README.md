# Marketing Campaign Analysis — Graduation Project

## Scenario
A marketing team runs campaigns across paid social, search, and email channels. It wants to understand spend, traffic, conversions, acquisition cost, and return on ad spend. Data is synthetic for classroom use.

## Files
- `marketing_campaign_raw.csv`: intentionally messy campaign data.
- `app.py`: interactive Streamlit dashboard.
- `analysis_starter.py`: guided examples using NumPy, Pandas, Matplotlib, Seaborn, and Plotly.
- `trainer_guide.pdf`: challenge-based two-hour lesson plan with hints and KPI definitions.
- `requirements.txt`: required packages.

## Run
`pip install -r requirements.txt`
`streamlit run app.py`

Keep `marketing_campaign_raw.csv` in the same folder as `app.py`.

## KPI caution
Use ratios of totals for aggregate CTR, conversion rate, CPA, and ROAS. Do not compare awareness campaigns and conversion campaigns with one KPI alone. Confirm suspicious spend and conversion values against the ad platform before changing production data.
