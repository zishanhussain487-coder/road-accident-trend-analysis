import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Road Accident Trend Analysis", page_icon="🚦", layout="wide")

st.title("🚦 Road Accident Trend Analysis")
st.caption("Explore accident frequency, injuries, fatalities, severity, and regional differences.")

st.sidebar.header("1. Load dataset")
uploaded = st.sidebar.file_uploader("Upload Government of India accident data (CSV or Excel)", type=["csv", "xlsx", "xls"])

@st.cache_data
def read_data(file_bytes, filename):
    import io
    bio = io.BytesIO(file_bytes)
    if filename.lower().endswith(".csv"):
        # Try common encodings and separators
        for enc in ("utf-8", "utf-8-sig", "cp1252", "latin1"):
            try:
                bio.seek(0)
                return pd.read_csv(bio, encoding=enc, sep=None, engine="python")
            except Exception:
                pass
        bio.seek(0)
        return pd.read_csv(bio)
    return pd.read_excel(bio)

def normalize_name(s):
    return "".join(ch.lower() for ch in str(s) if ch.isalnum())

def find_col(columns, hints):
    norm = {c: normalize_name(c) for c in columns}
    for hint in hints:
        for c, n in norm.items():
            if hint in n:
                return c
    return None

def to_numeric_clean(series):
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")
    return pd.to_numeric(
        series.astype(str).str.replace(",", "", regex=False).str.replace("%", "", regex=False).str.strip(),
        errors="coerce"
    )

def safe_sum(df, col):
    return float(df[col].fillna(0).sum()) if col else None

if uploaded is None:
    st.info("Upload the dataset provided by your hackathon organizer to begin. The app does not invent findings; charts and conclusions are calculated from your uploaded data.")
    st.subheader("What this dashboard includes")
    c1, c2, c3 = st.columns(3)
    c1.metric("Data quality", "Missing • Duplicates • Numeric checks")
    c2.metric("Analysis", "Accidents • Fatalities • Injuries")
    c3.metric("Outputs", "Clean CSV • Cleaning report")
    st.markdown("""
    **Expected input:** CSV or Excel file containing accident statistics. Column names can vary; the app tries to detect common names such as `State`, `Year`, `Total Accidents`, `Persons Killed`, and `Persons Injured`.

    **Important:** If the dataset has no population, registered-vehicle, or road-length denominator, the dashboard will not claim to calculate normalized rates.
    """)
    st.stop()

try:
    original = read_data(uploaded.getvalue(), uploaded.name)
except Exception as e:
    st.error(f"Could not read the file: {e}")
    st.stop()

if original.empty:
    st.error("The uploaded dataset has no rows.")
    st.stop()

df = original.copy()
df.columns = [str(c).strip() for c in df.columns]
rows_before, cols_before = df.shape
duplicate_count = int(df.duplicated().sum())
missing_before = int(df.isna().sum().sum())

# Standardize whitespace in text cells; keep original column names.
for c in df.select_dtypes(include=["object"]).columns:
    df[c] = df[c].astype(str).str.strip().replace({"": np.nan, "nan": np.nan, "None": np.nan, "NA": np.nan, "N/A": np.nan})

# Detect likely fields; let user override.
cols = list(df.columns)
year_guess = find_col(cols, ["year"])
region_guess = find_col(cols, ["state", "region", "district", "ut", "city"])
acc_guess = find_col(cols, ["totalaccident", "accidents", "numberofaccident", "noofaccident"])
fatal_guess = find_col(cols, ["personskilled", "fatalit", "death", "killed"])
injury_guess = find_col(cols, ["personsinjured", "injur", "wounded"])
population_guess = find_col(cols, ["population", "pop"])
vehicle_guess = find_col(cols, ["registeredvehicle", "vehiclepopulation", "vehicles"])
road_guess = find_col(cols, ["roadlength", "lengthofroad", "roadkm"])

st.sidebar.header("2. Map columns")
def choose(label, guess, allow_none=True):
    options = (["— Not available —"] if allow_none else []) + cols
    default = (["— Not available —"].index("— Not available —") if allow_none and guess is None
               else (options.index(guess) if guess in options else 0))
    selected = st.sidebar.selectbox(label, options, index=default)
    return None if selected == "— Not available —" else selected

year_col = choose("Year column", year_guess)
region_col = choose("Geographic region column", region_guess)
acc_col = choose("Accident count column", acc_guess)
fatal_col = choose("Fatalities / persons killed", fatal_guess)
injury_col = choose("Injuries / persons injured", injury_guess)
population_col = choose("Population (optional)", population_guess)
vehicle_col = choose("Registered vehicles (optional)", vehicle_guess)
road_col = choose("Road length (optional)", road_guess)

# Convert mapped numeric columns and likely numeric-looking columns.
numeric_cols = set([c for c in [year_col, acc_col, fatal_col, injury_col, population_col, vehicle_col, road_col] if c])
for c in numeric_cols:
    df[c] = to_numeric_clean(df[c])

# Remove exact duplicate rows and log this transformation.
df = df.drop_duplicates().copy()
# Flag negatives rather than silently changing the values.
negative_counts = {}
for c in [acc_col, fatal_col, injury_col, population_col, vehicle_col, road_col]:
    if c:
        negative_counts[c] = int((df[c] < 0).sum())

# Filters
st.sidebar.header("3. Filters")
filtered = df.copy()
if year_col and df[year_col].notna().any():
    years = sorted(df[year_col].dropna().unique().tolist())
    if len(years) > 1:
        selected_years = st.sidebar.multiselect("Year", years, default=years)
        filtered = filtered[filtered[year_col].isin(selected_years)]
if region_col and df[region_col].notna().any():
    regions = sorted(df[region_col].dropna().astype(str).unique().tolist())
    selected_regions = st.sidebar.multiselect("Region", regions, default=regions)
    filtered = filtered[filtered[region_col].astype(str).isin(selected_regions)]

st.subheader("Overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Records in view", f"{len(filtered):,}")
m2.metric("Accidents", f"{safe_sum(filtered, acc_col):,.0f}" if acc_col else "Not mapped")
m3.metric("Fatalities", f"{safe_sum(filtered, fatal_col):,.0f}" if fatal_col else "Not mapped")
m4.metric("Injuries", f"{safe_sum(filtered, injury_col):,.0f}" if injury_col else "Not mapped")

if acc_col and fatal_col:
    filtered["Fatalities per 100 accidents"] = np.where(
        filtered[acc_col] > 0, filtered[fatal_col] / filtered[acc_col] * 100, np.nan
    )
    severity = filtered[fatal_col].sum() / filtered[acc_col].sum() * 100 if filtered[acc_col].sum() > 0 else np.nan
    st.caption(f"Fatalities per 100 accidents (aggregate): {severity:.2f}" if pd.notna(severity) else "Fatalities per 100 accidents: not calculable (accident total is zero or missing).")
elif fatal_col:
    st.caption("Severity measure unavailable because no accident-count column is mapped.")

st.subheader("Data quality and cleaning")
q1, q2, q3, q4 = st.columns(4)
q1.metric("Rows in original file", f"{rows_before:,}")
q2.metric("Exact duplicate rows removed", f"{duplicate_count:,}")
q3.metric("Missing cells before cleaning", f"{missing_before:,}")
q4.metric("Rows after deduplication", f"{len(df):,}")

with st.expander("Missing values by column"):
    missing_table = pd.DataFrame({
        "Column": df.columns,
        "Missing values": [int(df[c].isna().sum()) for c in df.columns],
        "Missing %": [round(float(df[c].isna().mean() * 100), 2) for c in df.columns],
        "Data type": [str(df[c].dtype) for c in df.columns]
    }).sort_values("Missing values", ascending=False)
    st.dataframe(missing_table, use_container_width=True, hide_index=True)

with st.expander("Negative values in mapped measures (review required)"):
    if negative_counts:
        st.dataframe(pd.DataFrame([{"Measure": k, "Negative values": v} for k, v in negative_counts.items()]), use_container_width=True, hide_index=True)
        st.write("Negative counts are flagged for review; they are not automatically changed because the correct treatment depends on the source documentation.")
    else:
        st.write("No numeric measure columns mapped.")

st.subheader("Trend analysis")
if year_col:
    group_cols = [year_col]
    trend_data = filtered.groupby(group_cols, dropna=False).agg(
        **({ "Accidents": (acc_col, "sum")} if acc_col else {}),
        **({ "Fatalities": (fatal_col, "sum")} if fatal_col else {}),
        **({ "Injuries": (injury_col, "sum")} if injury_col else {})
    ).reset_index()
    metric_options = [x for x in ["Accidents", "Fatalities", "Injuries"] if x in trend_data.columns]
    if metric_options:
        metric = st.selectbox("Trend measure", metric_options)
        fig = px.line(trend_data.sort_values(year_col), x=year_col, y=metric, markers=True, title=f"{metric} by {year_col}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Map at least one accidents, fatalities, or injuries column to draw a trend.")
else:
    st.info("A year column was not detected or selected, so a time trend cannot be shown.")

st.subheader("Regional comparison")
if region_col:
    agg = {}
    if acc_col: agg["Accidents"] = (acc_col, "sum")
    if fatal_col: agg["Fatalities"] = (fatal_col, "sum")
    if injury_col: agg["Injuries"] = (injury_col, "sum")
    if agg:
        regional = filtered.groupby(region_col, dropna=False).agg(**agg).reset_index()
        chosen_measure = st.selectbox("Compare regions by", list(agg.keys()), key="regional_measure")
        regional = regional.sort_values(chosen_measure, ascending=False).head(20)
        fig = px.bar(regional, x=region_col, y=chosen_measure, title=f"Top regions by {chosen_measure}", labels={region_col: "Region"})
        fig.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(regional, use_container_width=True, hide_index=True)
    else:
        st.warning("Map at least one measure column to compare regions.")
else:
    st.info("Map a state, district, or region column to compare geography.")

st.subheader("Severity and normalized measures")
if acc_col and fatal_col:
    total_acc = filtered[acc_col].sum()
    total_fatal = filtered[fatal_col].sum()
    if total_acc > 0:
        st.metric("Fatalities per 100 accidents", f"{total_fatal / total_acc * 100:.2f}")
    else:
        st.warning("Severity ratio cannot be calculated because total accidents are zero or missing.")
if acc_col and injury_col:
    total_acc = filtered[acc_col].sum()
    if total_acc > 0:
        st.metric("Injuries per 100 accidents", f"{filtered[injury_col].sum() / total_acc * 100:.2f}")
if population_col and fatal_col:
    pop_sum = filtered[population_col].sum()
    if pop_sum > 0:
        st.metric("Fatalities per 100,000 population", f"{filtered[fatal_col].sum() / pop_sum * 100000:.2f}")
if vehicle_col and fatal_col:
    veh_sum = filtered[vehicle_col].sum()
    if veh_sum > 0:
        st.metric("Fatalities per 100,000 registered vehicles", f"{filtered[fatal_col].sum() / veh_sum * 100000:.2f}")
if road_col and fatal_col:
    road_sum = filtered[road_col].sum()
    if road_sum > 0:
        st.metric("Fatalities per 1,000 road-length units", f"{filtered[fatal_col].sum() / road_sum * 1000:.2f}")
st.caption("Normalized measures are shown only when the corresponding denominator column is mapped. Confirm denominator units and year alignment before interpreting them.")

st.subheader("Evidence-based findings")
findings = []
if acc_col and region_col and len(filtered):
    regsum = filtered.groupby(region_col)[acc_col].sum().sort_values(ascending=False)
    if len(regsum):
        findings.append(f"Highest accident-count region in the current filter: {regsum.index[0]} ({regsum.iloc[0]:,.0f} accidents).")
if fatal_col and region_col and len(filtered):
    regsum = filtered.groupby(region_col)[fatal_col].sum().sort_values(ascending=False)
    if len(regsum):
        findings.append(f"Highest fatalities region in the current filter: {regsum.index[0]} ({regsum.iloc[0]:,.0f} fatalities).")
if injury_col and region_col and len(filtered):
    regsum = filtered.groupby(region_col)[injury_col].sum().sort_values(ascending=False)
    if len(regsum):
        findings.append(f"Highest injuries region in the current filter: {regsum.index[0]} ({regsum.iloc[0]:,.0f} injuries).")
if year_col and acc_col and len(filtered):
    yr = filtered.groupby(year_col)[acc_col].sum().sort_index()
    if len(yr) >= 2:
        first, last = yr.iloc[0], yr.iloc[-1]
        change = ((last-first)/first*100) if first else np.nan
        if pd.notna(change):
            findings.append(f"Accidents changed by {change:.1f}% from {yr.index[0]} ({first:,.0f}) to {yr.index[-1]} ({last:,.0f}) in the selected data.")
if findings:
    for f in findings:
        st.write("• " + f)
else:
    st.write("Map the relevant columns and apply filters to generate numerical findings.")

st.subheader("Download outputs")
csv = df.to_csv(index=False).encode("utf-8-sig")
st.download_button("⬇️ Download cleaned dataset (CSV)", csv, file_name="cleaned_road_accident_data.csv", mime="text/csv")
report_lines = [
    "ROAD ACCIDENT TREND ANALYSIS — DATA-CLEANING DOCUMENTATION",
    f"Source file: {uploaded.name}",
    f"Original rows: {rows_before}",
    f"Original columns: {cols_before}",
    f"Exact duplicate rows detected and removed: {duplicate_count}",
    f"Missing cells before cleaning: {missing_before}",
    f"Rows after exact duplicate removal: {len(df)}",
    "",
    "Cleaning steps:",
    "1. Trimmed leading/trailing whitespace from column names and text values.",
    "2. Converted mapped measure columns to numeric values; unparseable values become missing.",
    "3. Treated blank text and common NA markers as missing.",
    "4. Removed exact duplicate rows.",
    "5. Flagged negative values in mapped measures for review; did not silently overwrite them.",
    "",
    "Limitations:",
    "- Findings reflect only the uploaded dataset and its reporting coverage.",
    "- Missing or inconsistent records may affect totals and comparisons.",
    "- Counts do not account for population, traffic volume, registered vehicles, or road length unless denominator data is available and correctly aligned.",
    "- Fatalities per 100 accidents is a descriptive severity indicator, not an individual crash-risk estimate.",
    "- Correlation or regional differences do not prove causation.",
    "- Column mapping should be checked against the official data dictionary."
]
report = "\n".join(report_lines).encode("utf-8")
st.download_button("⬇️ Download data-cleaning documentation (TXT)", report, file_name="data_cleaning_documentation.txt", mime="text/plain")

st.subheader("Dataset preview")
st.dataframe(filtered.head(100), use_container_width=True)
