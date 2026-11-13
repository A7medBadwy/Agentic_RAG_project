import re
from rank_bm25 import BM25Okapi
from app.services.vector_store import dense_search, all_payload_chunks

class RetrieverAgent:
    def retrieve(self, query: str, limit: int = 12, document_name: str | None = None):
        dense = dense_search(query, limit=limit * 2, document_name=document_name)
        corpus = all_payload_chunks()
        if document_name:
            corpus = [x for x in corpus if x.get("document_name") == document_name]
        tokens = [re.findall(r"\w+", x.get("text", "").lower()) for x in corpus]
        query_tokens = re.findall(r"\w+", query.lower())
        keyword_ranked = []
        if corpus and query_tokens:
            bm25 = BM25Okapi(tokens)
            scores = bm25.get_scores(query_tokens)
            keyword_ranked = [
                {**corpus[i], "keyword_score": float(scores[i])}
                for i in sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
                if scores[i] > 0
            ][:limit * 2]

        # Reciprocal Rank Fusion combines dense and lexical rankings.
        fused = {}
        for rank, item in enumerate(dense, 1):
            key = item.get("chunk_id")
            fused.setdefault(key, dict(item, rrf=0.0))
            fused[key]["rrf"] += 1 / (60 + rank)
        for rank, item in enumerate(keyword_ranked, 1):
            key = item.get("chunk_id")
            fused.setdefault(key, dict(item, rrf=0.0))
            fused[key]["rrf"] += 1 / (60 + rank)
        return sorted(fused.values(), key=lambda x: x["rrf"], reverse=True)[:limit]

    def rewrite_query(self, question: str) -> str:
        # Lightweight deterministic rewrite; replace with an LLM rewrite if desired.
        return " ".join(question.strip().split())
