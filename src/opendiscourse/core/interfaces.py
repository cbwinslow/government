from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class VectorStore(ABC):
    """
    Abstract interface for Vector databases (e.g., Qdrant, Pinecone, pgvector).
    Allows the platform to remain infrastructure-agnostic.
    """
    
    @abstractmethod
    def create_collection(self, collection_name: str, dimension: int) -> bool:
        """Create a new vector collection."""
        pass

    @abstractmethod
    def upsert_vectors(self, collection_name: str, vectors: List[Dict[str, Any]]) -> bool:
        """
        Upsert vectors into the collection.
        vectors should be a list of dicts with 'id', 'vector', and 'payload'.
        """
        pass

    @abstractmethod
    def search(self, collection_name: str, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Search the collection using a query vector and return the top matches."""
        pass


class RelationalStore(ABC):
    """
    Abstract interface for Relational databases (e.g., PostgreSQL, SQLite, MySQL).
    Allows the platform to abstract away direct ORM usage for core ETL operations.
    """
    
    @abstractmethod
    def get_politician_by_id(self, internal_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a politician by our internal UUID/ID."""
        pass
        
    @abstractmethod
    def get_politician_by_external_id(self, external_system: str, external_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a politician using an external ID.
        external_system could be 'bioguide', 'fec', 'opensecrets', etc.
        """
        pass

    @abstractmethod
    def upsert_politician(self, politician_data: Dict[str, Any]) -> int:
        """Insert or update a politician record and return the internal ID."""
        pass

    @abstractmethod
    def insert_action(self, politician_id: int, action_data: Dict[str, Any]) -> bool:
        """Insert a new 'Action' (e.g. vote, trade, campaign contribution)."""
        pass

    @abstractmethod
    def insert_word(self, politician_id: int, word_data: Dict[str, Any]) -> bool:
        """Insert a new 'Word' (e.g. speech, tweet, press release)."""
        pass
