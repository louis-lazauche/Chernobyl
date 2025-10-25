import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def make_tables(df_raw: pd.DataFrame):
    """
    Clean and prepare derived tables from the raw dataframe.
    """

    df = df_raw.copy()

    # --- 1️⃣ Nettoyage de base ---
    # Supprimer les espaces ou caractères invisibles
    df.columns = df.columns.str.strip()
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # --- 2️⃣ Conversion des types ---
    # Convertir la colonne "Date" en datetime (format année/mois/jour)
    df["Date"] = pd.to_datetime(df["Date"], format="%y/%m/%d", errors="coerce")

    # Convertir les isotopes en numérique
    isotope_cols = ["I_131_(Bq/m3)", "Cs_134_(Bq/m3)", "Cs_137_(Bq/m3)"]
    for col in isotope_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", ".")              # remplace virgules par points
            .str.extract(r"(\d+\.\d+|\d+)")[0]  # extrait les nombres
            .astype(float)
        )

    # --- 3️⃣ Nettoyage des doublons ---
    df = df.drop_duplicates()

    # --- 4️⃣ Gestion des valeurs manquantes ---
    # Comptage avant remplissage
    missing_before = df[isotope_cols].isna().sum()

    # Option 1 : remplacer les valeurs manquantes par la moyenne par région
    if "Location" in df.columns:
        df[isotope_cols] = df.groupby("Location")[isotope_cols].transform(lambda x: x.fillna(x.mean()))
    # Option 2 : s'il reste des NaN → remplacer par la moyenne globale
    df[isotope_cols] = df[isotope_cols].fillna(df[isotope_cols].mean())

    # Comptage après remplissage
    missing_after = df[isotope_cols].isna().sum()

    # --- 5️⃣ Normalisation des isotopes ---
    scaler = MinMaxScaler()
    df_norm = df.copy()
    df_norm[[f"{col}_norm" for col in isotope_cols]] = scaler.fit_transform(df[isotope_cols])

    # --- 6️⃣ Conversion finale en int pour les colonnes originales ---
    df[isotope_cols] = df[isotope_cols].round().astype(int)

    # --- 7️⃣ Résumé du nettoyage ---
    print("✅ Dataset nettoyé :")
    print(f"   → {len(df)} lignes après suppression des doublons")
    print(f"   → valeurs manquantes (avant/après) :")
    print(pd.DataFrame({"avant": missing_before, "après": missing_after}))

    # --- 8️⃣ Tables dérivées ---
    tables = {
        "clean": df,                       # dataset propre
        "normalized": df_norm,             # version normalisée
        "timeseries": df.groupby("Date")[isotope_cols].mean().reset_index(),
        "by_region": df.groupby("Location")[isotope_cols].mean().reset_index(),
        "geo": df[["Latitude", "Longitude", "Location"] + isotope_cols]
    }

    return tables
