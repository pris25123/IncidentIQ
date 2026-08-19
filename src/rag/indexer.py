import os
import uuid
from pathlib import Path
from google import genai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from src.config import (
    GEMINI_API_KEY,
    QDRANT_URL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_DIMENSION,
)


def get_genai_client():
    return genai.Client(api_key=GEMINI_API_KEY)


def get_qdrant_client():
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def extract_metadata(file_path: Path) -> tuple[str, str, str]:
    """Derive doc_type, service, and title from file path and content."""
    category = file_path.parent.name  # runbooks, postmortems, services
    title = file_path.stem.replace("_", " ").title()
    service = "general"

    if "payment" in file_path.stem:
        service = "payment-service"
    elif "auth" in file_path.stem:
        service = "auth-service"
    elif "order" in file_path.stem:
        service = "order-service"
    elif "database" in file_path.stem or "db" in file_path.stem:
        service = "database-primary"

    return category, service, title


def index_knowledge_base():
    """Reads all operational markdown documents and indexes them in Qdrant Cloud."""
    print("Connecting to Qdrant Cloud...")
    qdrant = get_qdrant_client()
    genai_client = get_genai_client()

    # Ensure collection exists
    collections = [c.name for c in qdrant.get_collections().collections]
    if QDRANT_COLLECTION in collections:
        print(f"Recreating collection '{QDRANT_COLLECTION}'...")
        qdrant.delete_collection(collection_name=QDRANT_COLLECTION)

    qdrant.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(size=EMBEDDING_DIMENSION, distance=Distance.COSINE),
    )
    print(f"Collection '{QDRANT_COLLECTION}' created.")

    knowledge_root = Path(__file__).resolve().parent.parent.parent / "knowledge"
    md_files = list(knowledge_root.glob("**/*.md"))
    print(f"Found {len(md_files)} operational documents to index...")

    points = []
    for file_path in md_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        doc_type, service, title = extract_metadata(file_path)

        # Split document into meaningful sections or index as full chunk
        sections = [s.strip() for s in content.split("\n## ") if s.strip()]
        for idx, sec in enumerate(sections):
            chunk_content = sec if idx == 0 else f"## {sec}"
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{file_path.name}_{idx}"))

            # Generate embedding
            res = genai_client.models.embed_content(
                model=EMBEDDING_MODEL_NAME,
                contents=chunk_content,
            )
            vector = res.embeddings[0].values

            payload = {
                "title": title,
                "file_name": file_path.name,
                "doc_type": doc_type,
                "service": service,
                "source": f"knowledge/{file_path.relative_to(knowledge_root).as_posix()}",
                "content": chunk_content,
            }

            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            )

    print(f"Upserting {len(points)} vector points into Qdrant Cloud...")
    qdrant.upsert(
        collection_name=QDRANT_COLLECTION,
        points=points,
    )
    print("Operational knowledge base indexed successfully in Qdrant Cloud!")


if __name__ == "__main__":
    index_knowledge_base()
