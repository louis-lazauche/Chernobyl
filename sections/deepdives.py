import streamlit as st
import pandas as pd
from typing import Optional
import pydeck as pdk

def render_insights(deck: pdk.Deck, df_filtered: Optional[pd.DataFrame]):
	"""Render the Insights narrative: show map, diagnostics and allow CSV export."""
	st.header("Insights — What the data reveals")
	st.markdown(
		"- Key observations: some stations show pronounced spikes on specific dates.\n"
		"- Very small values or entries marked '<'/'N' are treated as non-numeric and excluded.\n"
		"- Use the debug expander if no points appear on the map."
	)
	st.subheader("Interactive map — Regional view")
	st.markdown("The date slider in the sidebar selects the date; the map shows stations with valid measurements on that day.")
	# show deck (can be empty)
	st.pydeck_chart(deck)
	# export
	if df_filtered is not None and not df_filtered.empty:
		csv = df_filtered.to_csv(index=False)
		st.download_button("Download visible points (CSV)", data=csv, file_name="map_points.csv", mime="text/csv")
	else:
		st.info("No points visible to export for the selected date/isotope.")
