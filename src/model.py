from sentence_transformers import SentenceTransformer

# Load lightweight embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed(texts):
    return model.encode(texts, convert_to_tensor=True)
