#!/usr/bin/env -S uv run python
"""Qdrant infrastructure setup for government data embeddings."""

import os
import json
import glob
from pathlib import Path
from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer


# Configuration
QDRANT_URL = "http://172.25.10.64:6333"
COLLECTION_NAME = "congress_bills"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dimensions, fast for development
# For production: "BAAI/bge-large-en-v1.5"  # 1024 dimensions

# Data paths
CONGRESS_DATA_DIR = Path("congress/congress-data")


def get_qdrant_client() -> QdrantClient:
    """Initialize Qdrant client with ZeroTier endpoint."""
    return QdrantClient(url=QDRANT_URL)


def create_collection(
    client: QdrantClient, collection_name: str, vector_size: int = 1024
) -> bool:
    """Create a Qdrant collection for bill embeddings."""
    try:
        # Check if collection exists
        collections = client.get_collections()
        existing_names = [c.name for c in collections.collections]

        if collection_name in existing_names:
            print(f"Collection '{collection_name}' already exists")
            return True

        # Create new collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        print(f"Created collection '{collection_name}' with {vector_size} dimensions")
        return True
    except Exception as e:
        print(f"Error creating collection: {e}")
        return False


def load_bill_data() -> List[Dict[str, Any]]:
    """Load all bill JSON files from congress data directory."""
    bills = []

    # Find all data.json files in bill directories
    for data_file in glob.glob(f"{CONGRESS_DATA_DIR}/*/*/*/*/data.json"):
        try:
            with open(data_file, "r") as f:
                bill = json.load(f)
                # Add file path for reference
                bill["_source_path"] = data_file
                bills.append(bill)
        except Exception as e:
            print(f"Error loading {data_file}: {e}")

    print(f"Loaded {len(bills)} bills from {CONGRESS_DATA_DIR}")
    return bills


def prepare_text_for_embedding(bill: Dict[str, Any]) -> str:
    """Prepare bill text for embedding - combines key fields."""
    parts = [
        f"Bill {bill.get('bill_id', '')}: {bill.get('official_title', '')}",
        f"Type: {bill.get('bill_type', '')}",
        f"Congress: {bill.get('congress', '')}",
        f"Status: {bill.get('status', '')}",
    ]

    # Add summary if available (handle None case)
    summary = bill.get("summary")
    if summary and isinstance(summary, dict) and summary.get("text"):
        parts.append(f"Summary: {summary['text']}")

    # Add subjects
    if bill.get("subjects"):
        parts.append(f"Subjects: {', '.join(bill['subjects'])}")

    # Add sponsor info
    sponsor = bill.get("sponsor")
    if sponsor and isinstance(sponsor, dict) and sponsor.get("name"):
        parts.append(
            f"Sponsor: {sponsor.get('name')} ({sponsor.get('state')}-{sponsor.get('district')})"
        )

    return "\n".join(parts)


def generate_embeddings(
    bills: List[Dict[str, Any]], model: SentenceTransformer
) -> List[tuple]:
    """Generate embeddings for all bills."""
    texts = [prepare_text_for_embedding(bill) for bill in bills]

    print(f"Generating embeddings for {len(texts)} bills...")
    embeddings = model.encode(texts, show_progress_bar=True)

    return list(zip(bills, embeddings))


def upload_to_qdrant(
    client: QdrantClient, collection_name: str, bill_embeddings: List[tuple]
) -> int:
    """Upload bill embeddings to Qdrant."""
    points = []

    for idx, (bill, embedding) in enumerate(bill_embeddings):
        summary = bill.get("summary") or {}
        sponsor = bill.get("sponsor") or {}

        point = PointStruct(
            id=idx,
            vector=embedding.tolist(),
            payload={
                "bill_id": bill.get("bill_id"),
                "bill_type": bill.get("bill_type"),
                "congress": bill.get("congress"),
                "number": bill.get("number"),
                "official_title": bill.get("official_title"),
                "status": bill.get("status"),
                "introduced_at": bill.get("introduced_at"),
                "subjects": bill.get("subjects", []),
                "sponsor_name": sponsor.get("name"),
                "sponsor_state": sponsor.get("state"),
                "summary": summary.get("text", ""),
                "source_path": bill.get("_source_path"),
            },
        )
        points.append(point)

    # Upload in batches
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        client.upsert(collection_name=collection_name, points=batch)
        print(
            f"Uploaded batch {i // batch_size + 1}/{(len(points) + batch_size - 1) // batch_size}"
        )

    return len(points)


def main():
    """Main setup function."""
    print("=" * 50)
    print("Qdrant Infrastructure Setup")
    print("=" * 50)

    # Initialize client
    print(f"\nConnecting to Qdrant at {QDRANT_URL}...")
    client = get_qdrant_client()

    # List existing collections
    collections = client.get_collections()
    print(f"Existing collections: {[c.name for c in collections.collections]}")

    # Load embedding model
    print(f"\nLoading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    # Create collection
    vector_size = model.get_embedding_dimension()
    print(f"Model embedding dimension: {vector_size}")

    if not create_collection(client, COLLECTION_NAME, vector_size):
        print("Failed to create collection")
        return

    # Load bill data
    print("\nLoading bill data...")
    bills = load_bill_data()

    if not bills:
        print("No bills found to embed")
        return

    # Generate embeddings
    print("\nGenerating embeddings...")
    bill_embeddings = generate_embeddings(bills, model)

    # Upload to Qdrant
    print("\nUploading to Qdrant...")
    count = upload_to_qdrant(client, COLLECTION_NAME, bill_embeddings)

    print(f"\n{'=' * 50}")
    print(f"Successfully uploaded {count} bill embeddings to '{COLLECTION_NAME}'")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
