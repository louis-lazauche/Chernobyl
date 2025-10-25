import streamlit as st
import pandas as pd

def render_intro(max_row: pd.Series, decay_display: float, decay_direction: str):
	"""Render the intro title, context and always-visible KPIs.
	decay_display: non-negative percent magnitude for daily change
	decay_direction: 'increase'|'decrease'|'stable'|'N/A' used as caption
	"""
	st.title("Chernobyl Chemical Radiation Dashboard")
	st.markdown(
		"This dashboard shows temporal and spatial airborne concentrations of isotopes I-131, Cs-134 and Cs-137 following the Chernobyl accident."
	)
	# Key metrics always visible
	st.subheader("Key metrics")
	col_k1, col_k2, col_k3 = st.columns(3)
	col_k1.metric("Date of Peak Activity", max_row["Date"].strftime("%Y-%m-%d") if pd.notna(max_row.get("Date")) else "N/A")
	col_k2.metric("Max Concentration (Bq/m³)", f'{max_row["Concentration"]:.2f}' if pd.notna(max_row.get("Concentration")) else "N/A")
	col_k3.metric("Approx. Daily Change (%)", f"{decay_display:.2f}" if pd.notna(decay_display) else "N/A")
	col_k3.caption(f"Avg daily {decay_direction}")
