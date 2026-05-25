import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


def ensure_collection(name: str, size: int = 3072):
    client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"), api_key=os.getenv("QDRANT_API_KEY") or None)
    client.recreate_collection(collection_name=name, vectors_config=VectorParams(size=size, distance=Distance.COSINE))
    return client


if __name__ == "__main__":
    ensure_collection("politician_documents")
    print({"status": "ok", "collection": "politician_documents"})
