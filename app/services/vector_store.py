from functools import lru_cache
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from app.core.config import settings

@lru_cache(maxsize=1)
def get_embedder():
    return SentenceTransformer(settings.embedding_model)

@lru_cache(maxsize=1)
def get_client():
    return QdrantClient(path=settings.absolute_qdrant_path)

def ensure_collection():
    client = get_client()
    name = settings.collection_name
    if not client.collection_exists(name):
        dim = get_embedder().get_sentence_embedding_dimension()
        client.create_collection(
            collection_name=name,
            vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE)
        )

def upsert_chunks(chunks: list[dict]):
    if not chunks:
        return
    ensure_collection()
    embedder = get_embedder()
    vectors = embedder.encode([c["text"] for c in chunks], normalize_embeddings=True).tolist()
    points = []
    for chunk, vector in zip(chunks, vectors):
        payload = {k: v for k, v in chunk.items() if k != "id"}
        points.append(models.PointStruct(id=chunk["id"], vector=vector, payload=payload))
    get_client().upsert(collection_name=settings.collection_name, points=points)

def dense_search(query: str, limit: int | None = None, document_name: str | None = None):
    ensure_collection()
    vector = get_embedder().encode(query, normalize_embeddings=True).tolist()
    query_filter = None
    if document_name:
        query_filter = models.Filter(must=[
            models.FieldCondition(key="document_name", match=models.MatchValue(value=document_name))
        ])
    response = get_client().query_points(
        collection_name=settings.collection_name,
        query=vector,
        query_filter=query_filter,
        limit=limit or settings.top_k,
        with_payload=True
    )
    return [{"score": float(point.score), **(point.payload or {})} for point in response.points]

def delete_document(document_id: str):
    ensure_collection()
    get_client().delete(
        collection_name=settings.collection_name,
        points_selector=models.FilterSelector(
            filter=models.Filter(must=[
                models.FieldCondition(key="document_id", match=models.MatchValue(value=document_id))
            ])
        )
    )

def list_documents():
    ensure_collection()
    records, offset = [], None
    seen = {}
    while True:
        points, offset = get_client().scroll(
            collection_name=settings.collection_name, offset=offset,
            limit=256, with_payload=True, with_vectors=False
        )
        for point in points:
            p = point.payload or {}
            did = p.get("document_id")
            if did and did not in seen:
                seen[did] = {
                    "document_id": did,
                    "document_name": p.get("document_name"),
                    "file_type": p.get("file_type")
                }
        if offset is None:
            break
    return list(seen.values())

def all_payload_chunks():
    ensure_collection()
    output, offset = [], None
    while True:
        points, offset = get_client().scroll(
            collection_name=settings.collection_name, offset=offset,
            limit=512, with_payload=True, with_vectors=False
        )
        output.extend(p.payload or {} for p in points)
        if offset is None:
            break
    return output
