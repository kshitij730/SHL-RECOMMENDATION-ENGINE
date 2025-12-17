import re
import torch
from sentence_transformers.util import cos_sim
from src.model import embed
from src.utils import load_catalogue


# ------------------ LEXICAL SCORING (CHEAP + EFFECTIVE) ------------------ #

def lexical_overlap_score(query: str, text: str) -> float:
    q_tokens = set(query.split())
    t_tokens = set(text.lower().split())

    if not q_tokens:
        return 0.0

    return len(q_tokens & t_tokens) / len(q_tokens)


# ------------------ ENGINE ------------------ #

class RecommenderEngine:
    def __init__(self, catalogue_path="data/shl_assessments_full_catalog.csv"):
        # Load catalogue
        self.df = load_catalogue(catalogue_path)
        self.texts = self.df["full_text"].astype(str).tolist()

        # Load precomputed embeddings (FAST, SAFE)
        self.vectors = torch.load("data/embeddings.pt")

    # ================== PUBLIC API ================== #

    def recommend(self, query: str, top_k: int | None = None):
        query = self._clean_query(query)
        query_vec = embed([query])

        # ---------- SEMANTIC SIMILARITY ----------
        scores = cos_sim(query_vec, self.vectors)[0]

        # ---------- STRICT SEMANTIC FILTER ----------
        threshold = scores.mean() + scores.std() * 0.8
        candidate_idx = torch.where(scores >= threshold)[0]

        if len(candidate_idx) == 0:
            return []

        # ---------- RESULT COUNT CONTROL ----------
        if top_k is None:
            top_k = self._dynamic_top_k(len(query.split()), len(candidate_idx))

        # Overfetch slightly, then prune hard
        candidate_idx = candidate_idx[
            torch.argsort(scores[candidate_idx], descending=True)[:top_k * 3]
        ]

        # ---------- HYBRID SCORING ----------
        ALPHA = 0.75  # semantic weight
        BETA = 0.25   # lexical weight

        results = []
        for idx in candidate_idx:
            row = self.df.iloc[int(idx)]
            semantic_score = float(scores[idx])
            lexical_score = lexical_overlap_score(query, row["full_text"])

            final_score = (
                ALPHA * semantic_score +
                BETA * lexical_score
            )

            results.append({
                "name": row["Assessment Name"],
                "url": row["URL"],
                "description": row.get("Description", ""),
                "test_type": row.get("Test Type", ""),
                "duration": row.get("Assessment Duration", "N/A"),
                "remote_testing": row.get("Remote Testing Support", "N/A"),
                "adaptive": row.get("Adaptive/IRT Support", "N/A"),
                "score": round(final_score, 4)
            })

        # ---------- FINAL PRUNING ----------
        results.sort(key=lambda x: x["score"], reverse=True)

        # Relative confidence cutoff (kills weak tail)
        top_score = results[0]["score"]
        results = [
            r for r in results
            if r["score"] >= top_score * 0.6
        ]

        results = self._assign_confidence(results)
        return results[:top_k]

    # ================== CONFIDENCE ================== #

    def _assign_confidence(self, results):
        if not results:
            return results

        top_score = results[0]["score"]

        for r in results:
            if r["score"] >= top_score * 0.8:
                r["confidence"] = "High match"
            elif r["score"] >= top_score * 0.6:
                r["confidence"] = "Medium match"
            else:
                r["confidence"] = "Weak match"

        return results

    # ================== UTILITIES ================== #

    def _clean_query(self, query: str) -> str:
        query = query.lower()
        query = re.sub(r'[^a-z0-9\s]', ' ', query)
        return ' '.join(query.split())

    def _dynamic_top_k(self, query_len: int, candidates: int) -> int:
        if query_len < 5:
            return min(5, candidates)
        if query_len < 15:
            return min(7, candidates)
        return min(10, candidates)
