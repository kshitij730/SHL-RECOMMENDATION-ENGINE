import pandas as pd

def load_catalogue(path="data/shl_assessments_full_catalog.csv"):
    df = pd.read_csv(path)
    df = df.fillna("")  # Clean missing info
    df["full_text"] = (
        df["Assessment Name"].astype(str) + " " +
        df["Description"].astype(str) + " " +
        df["Test Type"].astype(str)
    )
    return df