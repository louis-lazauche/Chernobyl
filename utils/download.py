import os
import json
from pathlib import Path
import requests
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

DEFAULT_CANDIDATES = [
    DATA_DIR / "Chernobyl_Chemical_Radiation.csv",
    DATA_DIR / "Chernobyl_ Chemical_Radiation.csv",
]

def _read_seeds():
    seeds_path = ROOT / "seeds.json"
    if seeds_path.exists():
        try:
            return json.loads(seeds_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def get_data_path() -> Path:
    """
    Return path to cached CSV. If not present, try to download from:
    1) environment variable DATA_URL
    2) seeds.json['data_url']
    If no URL is provided and no local file exists, raise FileNotFoundError with instructions.
    """
    # 1) if a candidate local file exists, return it
    for p in DEFAULT_CANDIDATES:
        if p.exists():
            return p

    # 2) get URL from env or seeds.json
    url = os.environ.get("DATA_URL") or _read_seeds().get("data_url") or ""
    if not url:
        raise FileNotFoundError(
            "Data file not found in data/. Set DATA_URL env var or fill seeds.json 'data_url', or place the CSV in the data/ folder."
        )

    # determine destination filename
    seeds = _read_seeds()
    filename = seeds.get("download_filename", "Chernobyl_Chemical_Radiation.csv")
    dest = DATA_DIR / filename

    # if already downloaded (maybe incomplete), do not redownload
    if dest.exists():
        return dest

    # attempt download
    print(f"Downloading data from {url} to {dest} ...")
    try:
        resp = requests.get(url, stream=True, timeout=30)
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print("Download finished.")
        return dest
    except Exception as e:
        if dest.exists():
            return dest
        raise RuntimeError(f"Failed to download data from {url}: {e}") from e

if __name__ == "__main__":
    try:
        p = get_data_path()
        print(f"Using data file: {p}")
    except Exception as exc:
        print("Error:", exc, file=sys.stderr)
        sys.exit(1)
