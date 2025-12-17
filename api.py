from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.engine import RecommenderEngine

app = FastAPI()

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = RecommenderEngine()

class Query(BaseModel):
    query: str
    top_k: int # Allow up to 50, but engine will filter dynamically

@app.post("/recommend")
def recommend_api(payload: Query):
    recommendations = engine.recommend(payload.query, payload.top_k)
    return {
        "query": payload.query,
        "total_found": len(recommendations),
        "results": recommendations
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "SHL Assessment Recommender API is running"}