"""Database client wrappers for idempotent ingestion."""
import uuid
import hashlib
from typing import Dict, Any, List
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct

QDRANT_URL = "http://172.25.10.64:6333" # ZeroTier IP to user's native Qdrant instance

class DBClient:
    def __init__(self):
        self.qdrant = QdrantClient(url=QDRANT_URL)
        
    def generate_uuid(self, unique_string: str) -> str:
        """Generate a deterministic UUID from a unique string (e.g., a bill ID)."""
        hash_obj = hashlib.md5(unique_string.encode("utf-8"))
        return str(uuid.UUID(hash_obj.hexdigest()))

    def upsert_qdrant_point(self, collection_name: str, point_id_string: str, vector: List[float], payload: Dict[str, Any]) -> None:
        """
        Idempotently upsert a document into Qdrant. 
        If the deterministic UUID already exists, it is overwritten.
        """
        deterministic_uuid = self.generate_uuid(point_id_string)
        
        point = PointStruct(
            id=deterministic_uuid,
            vector=vector,
            payload=payload
        )
        
        self.qdrant.upsert(
            collection_name=collection_name,
            points=[point]
        )
        
    # TODO: Add Postgres ON CONFLICT DO UPDATE wrappers here
