from sentence_transformers import SentenceTransformer
import torch

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L12-v2",
            device="cpu"
        )
    return _model

def embed(texts):
    model = get_model()
    with torch.no_grad():
        return model.encode(
            texts,
            convert_to_tensor=True,
            batch_size=8,
            show_progress_bar=False
        )
