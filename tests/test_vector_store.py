from types import SimpleNamespace

import numpy as np

from app.services import vector_store


def test_dense_search_uses_query_points(monkeypatch):
    query = {}

    class Embedder:
        def encode(self, text, normalize_embeddings):
            assert text == "question"
            assert normalize_embeddings is True
            return np.array([0.1, 0.2])

    class Client:
        def query_points(self, **kwargs):
            query.update(kwargs)
            return SimpleNamespace(points=[
                SimpleNamespace(score=0.9, payload={"text": "supporting passage"})
            ])

    monkeypatch.setattr(vector_store, "ensure_collection", lambda: None)
    monkeypatch.setattr(vector_store, "get_embedder", lambda: Embedder())
    monkeypatch.setattr(vector_store, "get_client", lambda: Client())

    results = vector_store.dense_search("question", limit=3, document_name="notes.txt")

    assert results == [{"score": 0.9, "text": "supporting passage"}]
    assert query["query"] == [0.1, 0.2]
    assert query["limit"] == 3
    assert query["with_payload"] is True
    condition = query["query_filter"].must[0]
    assert condition.key == "document_name"
    assert condition.match.value == "notes.txt"
