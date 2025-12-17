import torch
import pandas as pd
from sentence_transformers import SentenceTransformer

CATALOGUE_PATH = "data/shl_assessments_full_catalog.csv"
OUTPUT_PATH = "data/embeddings.pt"

def main():
    df = pd.read_csv(CATALOGUE_PATH).fillna("")
    df["full_text"] = (
        df["Assessment Name"].astype(str) + " " +
        df["Description"].astype(str) + " " +
        df["Test Type"].astype(str)
    )

    texts = df["full_text"].tolist()

    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        device="cpu"
    )

    with torch.no_grad():
        embeddings = model.encode(
            texts,
            convert_to_tensor=True,
            batch_size=16,
            show_progress_bar=True
        )

    torch.save(embeddings, OUTPUT_PATH)
    print(f"Saved embeddings to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
