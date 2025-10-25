import pandas as pd
import streamlit as st
from . import download

@st.cache_data(show_spinner=True)
def load_data():
	"""Load the raw dataset (from cache or by downloading)."""
	path = download.get_data_path()
	df = pd.read_csv(path, dtype=str)
	return df


"""
Module for loading Chernobyl radiation data.

Dataset source:
- Title: Chernobyl Chemical Radiation CSV Country Data
- Author: brsdincer
- URL: https://www.kaggle.com/datasets/brsdincer/chernobyl-chemical-radiation-csv-country-data
- License: CC BY 4.0 (Creative Commons Attribution 4.0 International)

Usage of this dataset follows the terms of the above license.
"""
