.PHONY: install download run clean

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

download:
	python -m utils.download

run:
	streamlit run app.py

clean:
	# remove downloaded data files (be careful)
	rm -f data/Chernobyl_ Chemical_Radiation.csv data/Chernobyl_Chemical_Radiation.csv
