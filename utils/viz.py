import pandas as pd
import altair as alt
import pydeck as pdk

def build_line_chart(df_time: pd.DataFrame) -> alt.Chart:
	"""Return an Altair line chart for the timeseries dataframe."""
	return alt.Chart(df_time).mark_line().encode(
		x="Date:T",
		y="Concentration:Q",
		color="Isotope:N"
	).properties(height=300)

def build_half_life_chart() -> alt.Chart:
	"""Return an Altair bar chart displaying isotopes half-lives."""
	half_life = pd.DataFrame({
		"Isotope": ["I-131", "Cs-134", "Cs-137"],
		"Half-life (days)": [8, 754, 11000]
	})
	return alt.Chart(half_life).mark_bar().encode(
		x="Isotope",
		y="Half-life (days)",
		color="Isotope"
	)

def prepare_map_data(df_map: pd.DataFrame, selected_isotope: str, scale: float = 5000.0) -> pd.DataFrame:
	"""
	Coerce map columns, filter invalid rows and compute a numeric 'radius' column.
	Returns df_filtered (subset ready to send to pydeck).
	"""
	df_map_plot = df_map[["Latitude", "Longitude", "Location", selected_isotope, "Date"]].copy()
	df_map_plot = df_map_plot.rename(columns={selected_isotope: "Value"})
	# Coerce types safely
	df_map_plot["Latitude"] = pd.to_numeric(df_map_plot["Latitude"], errors="coerce")
	df_map_plot["Longitude"] = pd.to_numeric(df_map_plot["Longitude"], errors="coerce")
	df_map_plot["Value"] = pd.to_numeric(df_map_plot["Value"].astype(str).str.replace(",", "."), errors="coerce")
	# Filter invalid coords/values
	df_map_plot = df_map_plot.dropna(subset=["Latitude", "Longitude", "Value"])
	df_map_plot = df_map_plot[
		(df_map_plot["Latitude"].abs() <= 90) &
		(df_map_plot["Longitude"].abs() <= 180) &
		~((df_map_plot["Latitude"] == 0) & (df_map_plot["Longitude"] == 0))
	]
	# radius (scale multiplied by caller-specified factor)
	df_map_plot["radius"] = (df_map_plot["Value"].astype(float) + 1e-12) * scale
	return df_map_plot

def build_deck(df_filtered: pd.DataFrame, selected_isotope: str, default_center=(51.0, 30.0), zoom: int = 5) -> pdk.Deck:
	"""Build and return a pydeck.Deck object from prepared df_filtered."""
	color_map = {
		"I_131_(Bq/m3)": [255, 0, 0],
		"Cs_134_(Bq/m3)": [0, 255, 0],
		"Cs_137_(Bq/m3)": [0, 0, 255]
	}
	layer = pdk.Layer(
		"ScatterplotLayer",
		data=df_filtered,
		get_position=["Longitude", "Latitude"],
		get_radius="radius",
		get_fill_color=color_map.get(selected_isotope, [0, 0, 0]),
		pickable=True
	)
	# compute center robustly
	center_lat, center_lon = None, None
	if not df_filtered.empty:
		lat_mean = df_filtered["Latitude"].mean()
		lon_mean = df_filtered["Longitude"].mean()
		if pd.notna(lat_mean) and pd.notna(lon_mean):
			center_lat, center_lon = float(lat_mean), float(lon_mean)
	if center_lat is None:
		center_lat, center_lon = default_center
	view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=zoom, pitch=0)
	return pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "Location: {Location}\nValue: {Value}"})
