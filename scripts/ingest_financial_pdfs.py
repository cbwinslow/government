#!/usr/bin/env python3
"""LlamaIndex Ingestion Pipeline for Financial Disclosure PDFs."""

import os
import glob
import logging
from pathlib import Path

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ingest_pdfs():
    # 1. Ensure Qdrant collection exists for 1024-dim vectors
    logger.info("Connecting to Qdrant...")
    client = QdrantClient(url="http://172.25.10.64:6333")
    collection_name = "financial_pdfs"
    
    try:
        collections = client.get_collections()
        existing_names = [c.name for c in collections.collections]
        if collection_name not in existing_names:
            logger.info(f"Creating Qdrant collection '{collection_name}' with 1024 dimensions...")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
            )
    except Exception as e:
        logger.error(f"Error checking/creating collection: {e}")

    vector_store = QdrantVectorStore(client=client, collection_name=collection_name)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 2. Configure BAAI/bge-m3 (1024-dim) model via Ollama
    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.core import Settings

    logger.info("Routing Embeddings to Ollama Node (BAAI/bge-m3)...")
    embed_model = OllamaEmbedding(
        model_name="bge-m3",
        base_url="http://172.25.10.64:11434",
    )
    Settings.embed_model = embed_model
    # Set standard chunk size for text
    Settings.chunk_size = 2048
    Settings.chunk_overlap = 256

    # 3. Read the extracted PDFs
    base_dir = "/home/cbwinslow/workspace/government/financial-disclosures/extracted"
    
    # Just grabbing 2026 for the initial run to prove pipeline
    target_dir = os.path.join(base_dir, "2026")
    if not os.path.exists(target_dir):
        logger.error(f"Target directory {target_dir} not found.")
        return
        
    logger.info(f"Reading PDFs from {target_dir}...")
    documents = SimpleDirectoryReader(input_dir=target_dir, required_exts=[".xml", ".txt"]).load_data()
    # Import ledger utility
    import sys
    sys.path.append(os.path.dirname(__file__))
    from ledger_utils import log_file_ingestion

    logger.info(f"Loaded {len(documents)} document chunks from PDFs.")

    if not documents:
        logger.warning("No PDF documents found!")
        return

    # Log each unique file to the ledger
    unique_files = set()
    for doc in documents:
        if 'file_path' in doc.metadata:
            unique_files.add(doc.metadata['file_path'])
            
    for fpath in unique_files:
        log_file_ingestion(fpath, "financial_disclosures_xml", "VECTORIZED", {"collection": collection_name})

    # 4. Upsert into Qdrant
    logger.info("Upserting nodes to Qdrant VectorStore (this triggers the hardware embedding model)...")
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True
    )

    logger.info("Financial PDF ingestion complete!")

if __name__ == "__main__":
    ingest_pdfs()
