# Chernobyl Radiation Dashboard

Quick start

1. Create a virtual environment (recommended) and activate it.
2. Install pinned dependencies:
   - make install
   - or: python -m pip install -r requirements.txt
3. Provide the dataset:
   - Preferred: set DATA_URL environment variable to a direct CSV URL, then run:
     make download
   - Or place the CSV locally at `data/Chernobyl_Chemical_Radiation.csv` (or `data/Chernobyl_ Chemical_Radiation.csv`).
4. Run the app:
   - make run
   - or: streamlit run app.py

Notes

- The repository includes a simple download helper at `utils/download.py`. It caches the CSV in `data/`.
- If you don't want automatic download, manually add the CSV to the data/ folder.
- `seeds.json` contains a `data_url` placeholder and a few constants used for reproducible sampling.

## Written report

Purpose

- Provide an interactive dashboard to explore and visualize radiation measurements related to the Chernobyl accident, supporting spatial and temporal analysis of radiation levels.

Data used

- A CSV dataset with chemical and radiation measurements (expected at `data/Chernobyl_Chemical_Radiation.csv` or via the `DATA_URL` environment variable). Key columns include site identifiers, timestamps, and radiation values.

Technical choices

- Libraries: Streamlit for the UI, pandas for data processing, matplotlib/plotly for visualization. A small download helper (`utils/download.py`) handles retrieval and caching.
- Structure: a Streamlit entry point (`app.py`), a `data/` folder for sources, and separate utilities for downloading and preprocessing.
- Pipeline: data retrieval (or local load) → cleaning/minimization → reproducible sampling (`seeds.json`) → interactive visualization.

Analysis and insights

- Visualizations highlight hotspots and temporal trends; some stations show sharp spikes that warrant further investigation.
- The dataset contains outliers and gaps; robust preprocessing (filtering, interpolation) is recommended before advanced modeling.
- The dashboard is suitable for initial exploration and to guide deeper statistical or geospatial analyses.

Troubleshooting

- If the app complains about missing data, ensure either:
  - the file exists in data/, or
  - DATA_URL points to a reachable CSV and `make download` succeeded.


## Data Source and License
The dataset used in this dashboard is:
[Chernobyl Chemical Radiation CSV Country Data](https://www.kaggle.com/datasets/brsdincer/chernobyl-chemical-radiation-csv-country-data)  
by **brsdincer**, available under **CC BY 4.0 License**.
