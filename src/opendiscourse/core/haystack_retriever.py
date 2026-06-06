"""Haystack Retrieval Integration for OpenDiscourse."""

from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever

# We connect to the user's native Qdrant instance on port 6333
QDRANT_URL = "http://172.25.10.64:6333"

# State-of-the-art embedding model for dense/sparse/ColBERT retrieval
EMBEDDING_MODEL = "BAAI/bge-m3"

class CongressRetriever:
    def __init__(self, collection_name: str = "congress_bills"):
        self.document_store = QdrantDocumentStore(
            url=QDRANT_URL,
            index=collection_name,
            embedding_dim=1024, # Adjust based on the actual model used
        )
        
        self.retriever = QdrantEmbeddingRetriever(document_store=self.document_store)
        self.text_embedder = SentenceTransformersTextEmbedder(model=EMBEDDING_MODEL)
        
        # Build the Haystack Pipeline
        self.pipeline = Pipeline()
        self.pipeline.add_component("text_embedder", self.text_embedder)
        self.pipeline.add_component("retriever", self.retriever)
        
        self.pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
        
    def search(self, query: str, top_k: int = 5):
        """Execute a semantic search using Haystack."""
        result = self.pipeline.run({
            "text_embedder": {"text": query},
            "retriever": {"top_k": top_k}
        })
        return result["retriever"]["documents"]

if __name__ == "__main__":
    retriever = CongressRetriever()
    print("Haystack Pipeline successfully initialized.")
    # results = retriever.search("What is the latest bill on semiconductor manufacturing?")
    # print(results)
