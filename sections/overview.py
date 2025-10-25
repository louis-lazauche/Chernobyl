import streamlit as st
import altair as alt
import pandas as pd
from utils import viz

def render_analysis(line_chart: alt.Chart, df_map: pd.DataFrame, isotope_cols: list, max_row: pd.Series, decay_display: float, decay_direction: str):
	"""Render the Analysis narrative: trends + regional breakdown + half-life chart.
	decay_display: non-negative percent magnitude for daily change
	decay_direction: 'increase'|'decrease'|'stable'|'N/A'
	"""
	st.header("Analysis — Trends and regional breakdown")
	st.markdown("Explore temporal evolution of isotopes (chart) and compare regions.")
	st.subheader("Global Trends (daily series)")
	st.altair_chart(line_chart, use_container_width=True)
 
	# KPIs (convenience)
	col1, col2, col3 = st.columns(3)
	col1.metric("Date of Peak Activity", max_row["Date"].strftime("%Y-%m-%d") if pd.notna(max_row.get("Date")) else "N/A")
	col2.metric("Max Concentration (Bq/m³)", f'{max_row["Concentration"]:.2f}' if pd.notna(max_row.get("Concentration")) else "N/A")
	col3.metric("Approx. Daily Change (%)", f"{decay_display:.2f}" if pd.notna(decay_display) else "N/A")
	col3.caption(f"Avg daily {decay_direction}")
 
	st.markdown("Regional differences — Top 10 locations by total concentration for the selected date")
	df_region = df_map.copy()
	df_region["total"] = df_region[isotope_cols].sum(axis=1)
	top10 = df_region.groupby("Location")["total"].sum().nlargest(10).reset_index()
	bar_region = alt.Chart(top10).mark_bar().encode(
 		x="total:Q",
 		y=alt.Y("Location:N", sort="-x")
 	)
	st.altair_chart(bar_region, use_container_width=True)
 
	# half-life chart via viz helper
	st.subheader("Isotopes and their Half-life")
	st.altair_chart(viz.build_half_life_chart(), use_container_width=True)
