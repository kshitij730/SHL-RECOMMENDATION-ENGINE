from sentence_transformers import SentenceTransformer
import torch

# Load ONCE at import time
_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")

def embed(texts):
    with torch.no_grad():  # IMPORTANT: saves memory
        return _model.encode(
            texts,
            convert_to_tensor=True,
            batch_size=16,      # IMPORTANT: avoid spikes
            show_progress_bar=False
        )
