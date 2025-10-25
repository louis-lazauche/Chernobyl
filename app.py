import streamlit as st
import pandas as pd
import altair as alt
from utils.io import load_data
from utils.prep import make_tables
from sections import intro, overview, deepdives, conclusions
from utils import viz
import numpy as np

st.set_page_config(page_title="Chernobyl Radiation Dashboard", layout="wide")

# --- 1️⃣ Data loading and preparation ---
@st.cache_data(show_spinner=False)
def get_data():
	"""
	Load raw CSV and produce derived tables.

	Returns:
	- df_raw: pandas.DataFrame of original records (with Date parsed)
	- tables: dict of derived tables (e.g. 'clean', 'timeseries') produced by make_tables()

	This wrapper centralizes loading + minimal date parsing and drops rows with invalid dates.
	"""
	# Load raw dataframe and build derived tables
	df_raw = load_data()
	tables = make_tables(df_raw)

	# Ensure the "Date" column is parsed as datetime in each table and in df_raw
	for tbl in tables.values():
		if "Date" in tbl.columns:
			tbl["Date"] = pd.to_datetime(tbl["Date"], format="%y/%m/%d", errors="coerce")

	# Drop rows with invalid dates from df_raw
	df_raw["Date"] = pd.to_datetime(df_raw["Date"], format="%y/%m/%d", errors="coerce")
	df_raw = df_raw.dropna(subset=["Date"])  

	return df_raw, tables


# --- 2️⃣ Sidebar filters ---
raw, tables = get_data()
st.sidebar.header("Filters")

isotope_cols = ["I_131_(Bq/m3)", "Cs_134_(Bq/m3)", "Cs_137_(Bq/m3)"]

# Filter by isotope
selected_isotope = st.sidebar.selectbox(
	"Select isotope",
	isotope_cols,
	help="Choose which isotope column to visualize on the map and in charts. Example: Cs_137_(Bq/m3)."
)

# Filter by date
min_date = raw["Date"].min().date()
max_date = raw["Date"].max().date()
selected_date = st.sidebar.slider(
	"Select date",
	min_value=min_date,
	max_value=max_date,
	value=min_date,
	format="YYYY-MM-DD",
	help="Slide to pick a single date to filter map points and daily summaries (date-only match)."
)

# Filter the map data for the selected date
df_map = tables["clean"].copy()
df_map["Date"] = pd.to_datetime(df_map["Date"], format="%y/%m/%d", errors="coerce")
df_map = df_map.dropna(subset=["Date"])
# comparer uniquement la partie "date" (sans timestamp)
df_map = df_map[df_map["Date"].dt.date == selected_date]

# --- Prepare map data and deck using viz helpers (so sections can reuse them)
df_filtered = viz.prepare_map_data(df_map, selected_isotope, scale=1000.0 * 5)
with st.expander("Debug: map data diagnostics", expanded=False):
	st.write("Total rows after date filter:", len(df_map))
	st.write("Rows after numeric coercion and coord filter:", len(df_filtered))
	if len(df_filtered) > 0:
		st.dataframe(df_filtered[["Location", "Latitude", "Longitude", "Value", "radius"]].head(10))
	else:
		st.write("No valid rows for the selected date/isotope. Check that the chosen isotope column contains numeric values for that date.")

# Build deck (single object) for use in Insights
r = viz.build_deck(df_filtered, selected_isotope)
if df_filtered.empty:
	st.warning("No data points for the selected date and isotope. Try another date or isotope.")

# --- 3️⃣ Intro section ---
# Compute timeseries-derived dataframe and KPIs early so KPIs can be shown everywhere
df_time = tables["timeseries"].melt(id_vars="Date", value_vars=isotope_cols,
                                    var_name="Isotope", value_name="Concentration")

# Protect idxmax usage if all NaN
if df_time["Concentration"].dropna().empty:
	max_row = pd.Series({"Date": pd.NaT, "Concentration": float("nan")})
else:
	max_row = df_time.loc[df_time["Concentration"].idxmax()]

# --- Robust approx daily decay rate (log-difference per day) ---
def _approx_daily_decay_pct(df_time: pd.DataFrame) -> float:
	"""
	Estimate average daily percent change across isotopes.

	Doc: for debugging or explanation call st.help(_approx_daily_decay_pct)
	"""
	rates = []
	for name, g in df_time.groupby("Isotope"):
		g = g.sort_values("Date")
		vals = pd.to_numeric(g["Concentration"], errors="coerce")
		dates = pd.to_datetime(g["Date"], errors="coerce")
		dfg = pd.DataFrame({"Date": dates, "Val": vals}).dropna(subset=["Date", "Val"])
		# need positive values to compute logs
		dfg = dfg[dfg["Val"] > 0].copy()
		if len(dfg) < 2:
			continue
		dfg["delta_days"] = dfg["Date"].diff().dt.total_seconds() / 86400.0
		dfg["logdiff"] = np.log(dfg["Val"] / dfg["Val"].shift(1))
		dfg = dfg.dropna(subset=["delta_days", "logdiff"])
		# avoid zero-day intervals
		dfg = dfg[dfg["delta_days"] > 0]
		if dfg.empty:
			continue
		dfg["daily_log_rate"] = dfg["logdiff"] / dfg["delta_days"]
		# use median to reduce influence of outliers
		rates.append(dfg["daily_log_rate"].median())
	if not rates:
		return float("nan")
	avg_daily_log = float(np.mean(rates))
	# convert back to percent change per day
	return (np.exp(avg_daily_log) - 1.0) * 100.0

decay_rate = _approx_daily_decay_pct(df_time)

# Help expander exposing docstrings for key helpers and quick widget tips
with st.sidebar.expander("Help & function docs", expanded=False):
	st.write("Quick help for internal helpers and widget tips.")
	# show function docstrings / signatures for maintainers or curious users
	st.help(get_data)
	st.help(_approx_daily_decay_pct)
	st.caption("Widget tips: click the (i) help icon next to sidebar controls or hover over them where supported.")

# Present a non-negative user-facing metric and a direction label
if pd.isna(decay_rate):
	decay_display = float("nan")
	decay_direction = "N/A"
else:
	# decay_rate can be negative (net decrease), convert to magnitude for display
	decay_display = abs(float(decay_rate))
	if decay_rate < 0:
		decay_direction = "decrease"
	elif decay_rate > 0:
		decay_direction = "increase"
	else:
		decay_direction = "stable"

# Build the line chart object here so it is defined before narrative branches use it.
line_chart = alt.Chart(df_time).mark_line().encode(
    x="Date:T",
    y="Concentration:Q",
    color="Isotope:N"
).properties(height=300)

# Render intro section (title + KPIs) from the dedicated module
intro.render_intro(max_row, decay_display, decay_direction)

# --- Narrative controller (Problem → Analysis → Insights → Implications) ---
narrative_step = st.sidebar.radio(
	"Dashboard narrative",
	("Problem", "Analysis", "Insights", "Implications"),
	index=1
)

# Short guidance visible at top of main pane
st.markdown(f"**Mode:** {narrative_step} — follow the steps to understand the problem, analyze the data and derive conclusions.")

# --- Display content per narrative step ---
if narrative_step == "Problem":
	st.header("Problem — What happened?")
	st.markdown("""
	- An episode of atmospheric contamination was detected after the Chernobyl accident.
	- Central question: where and when were airborne concentrations highest?
	- Use the isotope selector and the date slider in the sidebar to focus on a specific isotope and date.
	""")
	st.subheader("Peak event summary")
	st.markdown(f"- Peak date observed (all stations, all isotopes): **{max_row['Date'].strftime('%Y-%m-%d')}**")
	st.markdown(f"- Maximum observed value: **{max_row['Concentration']:.2f} Bq/m³**")
	st.info("Switch to 'Analysis' to inspect trends and regional distribution.")

if narrative_step == "Analysis":
	# Delegate all Analysis rendering (trends, regional breakdown, half-life) to the overview section
	overview.render_analysis(line_chart, df_map, isotope_cols, max_row, decay_display, decay_direction)

if narrative_step == "Insights":
	deepdives.render_insights(r, df_filtered)

if narrative_step == "Implications":
	conclusions.render_implications()
