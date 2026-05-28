#!/usr/bin/env python3
"""
Haystack embedding pipeline using cbwwin RTX 3060 via Ollama API.
"""

import os
import json
import time
from pathlib import Path
from typing import List, Optional

import requests

try:
    from haystack import Document, Pipeline
    from haystack.components.embedders import OpenAIEmbeddingEncoder
    from haystack.document_stores import PgVectorDocumentStore
    from haystack.components.converters import TextFileToText
    from haystack.components.preprocessors import DocumentSplitter
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "haystack-ai[all]", "pgvector"], check=True)
    from haystack import Document, Pipeline
    from haystack.components.embedders import OpenAIEmbeddingEncoder
    from haystack.document_stores import PgVectorDocumentStore


class OllamaEmbeddingEncoder:
    """Haystack-compatible embedding encoder using Ollama API."""
    
    def __init__(self, model: str = "nomic-embed-text", url: str = None):
        self.model = model
        self.url = url or os.environ.get("OLLAMA_URL", "http://172.25.215.34:11434")
        self.dim = 768  # nomic-embed-text default
    
    def run(self, documents: List[Document]) -> List[Document]:
        """Generate embeddings for documents."""
        texts = [doc.content or "" for doc in documents]
        
        # Batch embed
        embeddings = []
        for text in texts:
            try:
                resp = requests.post(
                    f"{self.url}/api/embeddings",
                    json={"model": self.model, "prompt": text[:32000]},
                    timeout=180
                )
                if resp.status_code == 200:
                    embeddings.append(resp.json().get("embedding", []))
                else:
                    embeddings.append([])
            except Exception:
                embeddings.append([])
        
        for doc, emb in zip(documents, embeddings):
            if emb:
                doc.embedding = emb
        
        return documents
    
    def warm_up(self):
        """No warmup needed for API."""
        pass


def create_embedding_pipeline(db_url: str = None):
    """Create Haystack pipeline for embedding and storage."""
    db_url = db_url or os.environ.get("DATABASE_URL", "postgresql://postgres@localhost:5432/epstein")
    
    document_store = PgVectorDocumentStore(
        connection_string=db_url,
        vector_function="cosine",
        embedding_dimension=768,
        table_name="documents",
        search_kwargs={"k": 10}
    )
    
    return Pipeline()


def embed_dataset_haystack(
    input_file: Path,
    output_file: Path,
    batch_size: int = 100,
    use_cbwwin: bool = True
):
    """Embed dataset using Haystack with Ollama backend."""
    
    # Determine Ollama URL
    ollama_url = "http://172.25.215.34:11434" if use_cbwwin else "http://localhost:11434"
    
    # Test connection
    try:
        resp = requests.get(f"{ollama_url}/api/tags", timeout=10)
        print(f"Connected to Ollama at {ollama_url}")
    except Exception as e:
        print(f"Warning: Could not connect to {ollama_url}: {e}")
        print("Falling back to localhost...")
        ollama_url = "http://localhost:11434"
    
    encoder = OllamaEmbeddingEncoder(url=ollama_url)
    
    processed = 0
    errors = 0
    
    with open(input_file) as f_in, open(output_file, "w") as f_out:
        batch = []
        for i, line in enumerate(f_in):
            record = json.loads(line)
            batch.append(record)
            
            if len(batch) >= batch_size:
                docs = [Document(content=r.get("content", r.get("body", r.get("text", "")))) 
                        for r in batch if r.get("content") or r.get("body") or r.get("text")]
                
                embedded = encoder.run(docs)
                
                for doc, record in zip(embedded, batch):
                    if doc.embedding:
                        record["embedding"] = doc.embedding
                        record["embedding_dim"] = 768
                        f_out.write(json.dumps(record) + "\n")
                        processed += 1
                    else:
                        errors += 1
                
                print(f"  Processed {processed} samples ({errors} errors)...")
                batch = []
        
        # Process remaining
        if batch:
            docs = [Document(content=r.get("content", r.get("body", r.get("text", "")))) 
                    for r in batch if r.get("content") or r.get("body") or r.get("text")]
            embedded = encoder.run(docs)
            
            for doc, record in zip(embedded, batch):
                if doc.embedding:
                    record["embedding"] = doc.embedding
                    record["embedding_dim"] = 768
                    f_out.write(json.dumps(record) + "\n")
                    processed += 1
                else:
                    errors += 1
    
    print(f"Done: {processed} records, {errors} errors")
    return processed, errors


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: embed_haystack.py <input.jsonl> <output.jsonl>")
        sys.exit(1)
    
    embed_dataset_haystack(Path(sys.argv[1]), Path(sys.argv[2]))