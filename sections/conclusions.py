import streamlit as st

def render_implications():
	st.header("Implications & Recommendations")
	st.markdown("""
	What this dashboard teaches and its limitations:

	- What we learn:
	  * Temporality: visualize isotope time-series (spikes, decay).
	  * Spatiality: identify stations/regions with measured spikes on given dates.
	  * Isotopic comparison: comparing I-131, Cs-134 and Cs-137 helps infer deposition signatures and decay behavior.

	- Usefulness for understanding a nuclear accident:
	  * Useful to detect and localize episodes of atmospheric contamination and prioritize local investigations.
	  * Can support targeted public health actions (local alerts, additional sampling).

	- Important limitations:
	  * The dataset contains special encodings ('<', 'N', etc.) and missing values — those entries are excluded from numeric analyses.
	  * Measurements are point-samples (fixed stations): absence of a measurement does not imply absence of contamination nearby.
	  * Meteorological transport and dispersion are not modeled — attributing sources requires wind/trajectory data and dispersion modeling.

	Practical recommendations:
	  1. Perform thorough quality control to distinguish measurement errors from detection limits.
	  2. Combine observations with dispersion models and meteorological data to trace plume origins.
	  3. For public health, combine these measurements with dose assessments and intervention criteria.
	""")
	st.info("CSV export of the visible points is available in the 'Insights' tab (under the map).")
