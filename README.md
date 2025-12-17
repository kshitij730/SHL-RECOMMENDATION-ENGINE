# 🎯 SHL Assessment Recommender

A deterministic, explainable semantic recommendation system that helps HR professionals and recruiters identify the most relevant SHL assessments for a given hiring requirement.

This system is deliberately designed without generative AI or LLMs to ensure reproducibility, fairness, explainability, and reliability — key requirements in assessment and hiring platforms.

---
## 🎥 Demo Video

[![Demo Video](https://github.com/kshitij730/SHL-RECOMMENDATION-ENGINE/blob/main/SHL-RECOMMENDATION-ENGINE.mp4)

---
## 🔍 What This Project Does

- Takes a natural-language hiring requirement
- Finds semantically relevant SHL assessments
- Ranks them using industry-standard retrieval and reranking techniques
- Returns dynamic, confidence-labelled results
- Avoids hallucination, randomness, and black-box reasoning

---

## ✨ Key Features

### ✅ Semantic Search (Not Keyword Matching)
- Uses transformer-based sentence embeddings
- Understands intent beyond exact keywords
- Handles varied phrasing (e.g. "data analyst", "analytics role", "data-focused position")

### ✅ Two-Stage Ranking (Production-Grade)
**Bi-Encoder Retrieval**
- Fast semantic similarity search over the full catalog

**Cross-Encoder Reranking**
- Deep query–document relevance scoring
- Industry-standard approach used in search systems

### ✅ Dynamic Results (LLM-like Behavior, Deterministic)
- No fixed result count
- Result size adapts to query specificity
- Strong queries → fewer, higher-confidence results
- Broad queries → more alternatives

### ✅ Confidence Labels
Each recommendation is tagged with:
- High match
- Medium match
- Weak match

These labels are relative to the query, not arbitrary thresholds.

### ✅ Explainable & Auditable
- No generative reasoning
- No hallucinated output
- Rankings are reproducible and inspectable
- Suitable for hiring and assessment use cases

---

## 🚫 What This Project Explicitly Avoids

- ❌ No LLMs (GPT, Claude, etc.)
- ❌ No prompt engineering
- ❌ No non-deterministic outputs
- ❌ No opaque "AI decisions"

This is an engineering-first system, not a demo toy.

---

## 🏗️ Architecture Overview

![Architecture Overview](https://github.com/kshitij730/SHL-RECOMMENDATION-ENGINE/blob/main/RECOMMENDATION%20ENGINE%20ARCITECTURE.png)

---

## 🧠 Technology Stack

### Backend
- Python 3.11
- FastAPI (REST API)
- Uvicorn (ASGI server)

### ML / NLP
- Sentence Transformers
  - Bi-encoder for retrieval
  - Cross-encoder for reranking
- PyTorch
- Cosine similarity

### Frontend
- Vanilla HTML / CSS / JavaScript
- No framework dependencies
- Lightweight and fast

---

## 📦 Project Structure

```
shl-recommender/
│
├── src/
│   ├── model.py        # Embedding model loader
│   ├── engine.py       # Recommendation engine
│   └── utils.py        # CSV loading utilities
│
├── data/
│   └── shl_assessments_full_catalog.csv
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
│
├── api.py              # FastAPI application
├── requirements.txt
└── README.md
```

---

## 🚀 Running Locally

### 1. Create environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Start backend
```bash
uvicorn api:app --reload
```

**Backend:** http://127.0.0.1:8000  
**Swagger UI:** http://127.0.0.1:8000/docs

### 4. Start frontend
```bash
cd frontend
python -m http.server 8080
```

**Frontend:** http://localhost:8080

---

## 🔌 API Usage

### POST /recommend

**Request:**
```json
{
  "query": "Data analyst with strong numerical reasoning"
}
```

**Response:**
```json
{
  "query": "Data analyst with strong numerical reasoning",
  "total_found": 6,
  "results": [
    {
      "name": "Numerical Reasoning Test",
      "score": 0.87,
      "confidence": "High match"
    }
  ]
}
```

## 🎓 Why This Approach (Design Rationale)

This system intentionally avoids generative AI because:

- Hiring tools require fairness and reproducibility
- Rankings must be auditable
- Results must not change unpredictably
- Confidence must be grounded in measurable relevance

The architecture mirrors real-world enterprise search systems, not demo-level chatbots.

---

## 🌐 Deployment

### Backend (Render)
1. Push code to GitHub
2. Create account on [Render](https://render.com)
3. Connect repository
4. Deploy with provided `render.yaml`

### Frontend (Netlify)
1. Update `frontend/script.js` with your backend URL
2. Go to [Netlify](https://netlify.com)
3. Drag and drop `frontend` folder










