import re
import torch
from sentence_transformers import CrossEncoder
from sentence_transformers.util import cos_sim
from src.model import embed
from src.utils import load_catalogue


class RecommenderEngine:
    def __init__(self, catalogue_path="data/shl_assessments_full_catalog.csv"):
        self.df = load_catalogue(catalogue_path)

        # Ensure pure Python strings
        self.texts = self.df["full_text"].astype(str).tolist()

        # Bi-encoder embeddings (recall stage)
        self.vectors = embed(self.texts)

        # Cross-encoder reranker (deep relevance)
        self.reranker = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2",
            max_length=512
        )

        self.stop_words = {
            'a','an','the','and','or','but','in','on','at','to','for','of','with',
            'by','from','as','is','was','are','be','been','have','has','had'
        }

    # ================== PUBLIC API ================== #

    def recommend(self, query: str, top_k: int | None = None):
        query = self._clean_query(query)
        query_vec = embed([query])

        # ---------- BI-ENCODER RETRIEVAL ----------
        scores = cos_sim(query_vec, self.vectors)[0]

        # Dynamic cutoff: keep top 15% only
        scores_sorted = torch.sort(scores, descending=True).values
        cutoff = scores_sorted[int(len(scores_sorted) * 0.85)]
        candidate_idx = torch.where(scores >= cutoff)[0]

        if len(candidate_idx) == 0:
            return []

        if top_k is None:
            top_k = self._dynamic_top_k(len(query.split()), len(candidate_idx))

        recall_k = min(top_k * 5, len(candidate_idx))
        candidate_idx = candidate_idx[
            torch.argsort(scores[candidate_idx], descending=True)[:recall_k]
        ]

        # ---------- CROSS-ENCODER RERANK ----------
        pairs = []
        rows = []

        for idx in candidate_idx:
            row = self.df.iloc[int(idx)]
            pairs.append((query, row["full_text"]))
            rows.append(row)

        # Cross-encoder returns NumPy float32 → must cast
        raw_scores = [float(s) for s in self.reranker.predict(pairs)]

        norm_scores = self._normalize_scores(raw_scores)

        # ---------- BUILD RESULTS ----------
        results = []
        for row, score in zip(rows, norm_scores):
            results.append({
                "name": row["Assessment Name"],
                "url": row["URL"],
                "description": row.get("Description", ""),
                "test_type": row.get("Test Type", ""),
                "duration": row.get("Assessment Duration", "N/A"),
                "remote_testing": row.get("Remote Testing Support", "N/A"),
                "adaptive": row.get("Adaptive/IRT Support", "N/A"),
                "score": float(round(score, 4))  # 🔥 FASTAPI SAFE
            })

        # Sort by normalized score
        results.sort(key=lambda x: x["score"], reverse=True)

        # ---------- CONFIDENCE LABELS ----------
        results = self._assign_confidence(results)

        # ---------- DYNAMIC RESULT COUNT ----------
        top_score = results[0]["score"]
        results = [
            r for r in results
            if r["score"] >= top_score * 0.45
        ]

        return results[:top_k]

    # ================== CONFIDENCE ================== #

    def _assign_confidence(self, results):
        if not results:
            return results

        top_score = results[0]["score"]

        for r in results:
            if r["score"] >= top_score * 0.8:
                r["confidence"] = "High match"
            elif r["score"] >= top_score * 0.55:
                r["confidence"] = "Medium match"
            else:
                r["confidence"] = "Weak match"

        return results

    # ================== UTILITIES ================== #

    def _normalize_scores(self, scores):
        """
        Converts ALL values to Python float
        Ensures FastAPI JSON safety
        """
        scores = [float(s) for s in scores]

        min_s = min(scores)
        max_s = max(scores)

        if max_s == min_s:
            return [1.0 for _ in scores]

        return [
            float((s - min_s) / (max_s - min_s))
            for s in scores
        ]

    def _clean_query(self, query: str) -> str:
        query = query.lower()
        query = re.sub(r'[^a-z0-9\s]', ' ', query)
        return ' '.join(query.split())

    def _dynamic_top_k(self, query_len: int, candidates: int) -> int:
        if query_len < 5:
            return min(10, candidates)
        if query_len < 15:
            return min(20, candidates)
        return min(30, candidates)
