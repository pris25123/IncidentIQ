from google import genai
from qdrant_client import QdrantClient
from src.config import (
    GEMINI_API_KEY,
    QDRANT_URL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION,
    EMBEDDING_MODEL_NAME,
)

_genai_client = None
_qdrant_client = None


def get_genai():
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(api_key=GEMINI_API_KEY)
    return _genai_client


def get_qdrant():
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    return _qdrant_client


def retrieve_operational_knowledge(
    query: str,
    limit: int = 4,
    service_filter: str | None = None,
) -> list[dict]:
    """
    Performs semantic vector search over operational knowledge base (runbooks, postmortems, service docs)
    in Qdrant Cloud.
    """
    genai_client = get_genai()
    qdrant = get_qdrant()

    # Generate query embedding
    embed_response = genai_client.models.embed_content(
        model=EMBEDDING_MODEL_NAME,
        contents=query,
    )
    query_vector = embed_response.embeddings[0].values

    # Query Qdrant with query_points
    search_response = qdrant.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,
        limit=limit,
    )

    results = []
    points = search_response.points if hasattr(search_response, "points") else search_response
    for hit in points:
        payload = hit.payload or {}
        results.append(
            {
                "score": round(float(hit.score), 4) if hasattr(hit, "score") and hit.score is not None else 0.0,
                "title": payload.get("title", "Untitled Document"),
                "doc_type": payload.get("doc_type", "general"),
                "service": payload.get("service", "general"),
                "source": payload.get("source", ""),
                "content": payload.get("content", ""),
            }
        )

    return results
