from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import gc

app = FastAPI(title="SHL Assessment Recommender API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engine lazily to save memory during startup
engine = None

def get_engine():
    """Lazy load the recommender engine"""
    global engine
    if engine is None:
        from src.engine import RecommenderEngine
        engine = RecommenderEngine()
        # Force garbage collection after loading
        gc.collect()
    return engine

class Query(BaseModel):
    query: str
    top_k: int = 10

@app.get("/")
def root():
    return {
        "message": "SHL Assessment Recommender API",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "recommend": "/recommend (POST)"
        }
    }

@app.get("/health")
def health_check():
    try:
        eng = get_engine()
        return {
            "status": "healthy",
            "message": "SHL Assessment Recommender API is running",
            "assessments_loaded": len(eng.df)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": str(e)
        }

@app.post("/recommend")
def recommend_api(payload: Query):
    try:
        eng = get_engine()
        recommendations = eng.recommend(payload.query, payload.top_k)
        
        # Clean up after request to free memory
        gc.collect()
        
        return {
            "query": payload.query,
            "total_found": len(recommendations),
            "results": recommendations
        }
    except Exception as e:
        return {
            "error": str(e),
            "query": payload.query,
            "total_found": 0,
            "results": []
        }

@app.on_event("startup")
async def startup_event():
    """Preload model on startup"""
    print("🚀 Starting up...")
    # Preload the engine
    get_engine()
    print("✅ Engine loaded successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global engine
    engine = None
    gc.collect()
    print("👋 Shutting down...")
