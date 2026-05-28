#!/usr/bin/env python3
"""
Multi-provider embedding with Cohere, Gemini, and Ollama fallback.
Stores embeddings with their native dimensions (no truncation).
"""
import json
import os
import time
from pathlib import Path
from typing import List, Optional
import argparse

try:
    import cohere
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "cohere"], check=True)
    import cohere

try:
    import google.genai as genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


class CohereEmbedder:
    """Fast embedding client using Cohere API (1024 or 384 dim)."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("COHERE_API_KEY")
        self.client = cohere.ClientV2(api_key=self.api_key)
    
    def embed_batch(self, texts: List[str], batch_size: int = 96, light: bool = False) -> List[Optional[List[float]]]:
        model = 'embed-english-light-v3.0' if light else 'embed-english-v3.0'
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                result = self.client.embed(
                    texts=batch,
                    model=model,
                    input_type='search_document'
                )
                embeddings.extend(result.embeddings.float_)
            except Exception as e:
                print(f"  Cohere batch error: {e}")
                embeddings.extend([None] * len(batch))
        return embeddings


class GeminiEmbedder:
    """Embeddings client using Gemini API (configurable 768 dim)."""
    
    def __init__(self, api_key: str = None, dimension: int = 768):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "AIzaSyBqAWfHiUCVMROlMqwb9nc_Wptfo4-qTl4")
        self.dimension = dimension
        self.client = genai.Client(api_key=self.api_key) if HAS_GENAI else None
    
    def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        embeddings = []
        for text in texts:
            try:
                result = self.client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=text[:9000],
                    config=types.EmbedContentConfig(output_dimensionality=self.dimension)
                )
                embeddings.append(result.embeddings[0].values if result.embeddings else None)
            except Exception as e:
                print(f"  Gemini error: {e}")
                embeddings.append(None)
        return embeddings


class OllamaEmbedder:
    """Local embedding fallback using Ollama (768 dim)."""
    
    def __init__(self, url: str = None, model: str = "nomic-embed-text"):
        self.url = url or "http://localhost:11434/api/embeddings"
        self.model = model
    
    def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        import requests
        embeddings = []
        for text in texts:
            try:
                resp = requests.post(self.url, json={"model": self.model, "prompt": text[:32000]}, timeout=60)
                if resp.status_code == 200:
                    embeddings.append(resp.json().get("embedding", None))
                else:
                    embeddings.append(None)
            except Exception as e:
                embeddings.append(None)
        return embeddings


def process_file(input_file: Path, output_file: Path, backend: str = "cohere", 
               batch_size: int = 96, dimension: int = None) -> tuple[int, int]:
    """Process JSONL and add embeddings using specified backend."""
    
    embedder_kwargs = {}
    if backend == "cohere_light":
        embedder = CohereEmbedder()
        embedder.embed_batch = lambda texts: embedder.embed_batch(texts, light=True)
    elif backend == "cohere":
        embedder = CohereEmbedder()
    elif backend == "gemini":
        embedder = GeminiEmbedder(dimension=dimension or 768)
    else:
        embedder = OllamaEmbedder()
    
    processed, errors = 0, 0
    records_buffer, texts_buffer = [], []
    
    with open(input_file) as f_in, open(output_file, "w") as f_out:
        for line in f_in:
            record = json.loads(line)
            
            # Extract text from record
            text = record.get("content") or record.get("body") or record.get("text") or record.get("preview") or ""
            if "subject" in record and text:
                text = f"{record['subject']}\n\n{text}"
            
            records_buffer.append(record)
            texts_buffer.append(text)
            
            if len(texts_buffer) >= batch_size:
                embeddings = embedder.embed_batch(texts_buffer)
                
                for rec, emb in zip(records_buffer, embeddings):
                    if emb:
                        rec["embedding"] = emb
                        rec["embedding_dim"] = len(emb)
                        f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        processed += 1
                    else:
                        errors += 1
                
                records_buffer, texts_buffer = [], []
                
                if backend in ["gemini", "ollama"]:
                    time.sleep(0.65)  # Rate limit
        
        # Process remaining
        if texts_buffer:
            embeddings = embedder.embed_batch(texts_buffer)
            for rec, emb in zip(records_buffer, embeddings):
                if emb:
                    rec["embedding"] = emb
                    rec["embedding_dim"] = len(emb)
                    f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    processed += 1
                else:
                    errors += 1
    
    print(f"Done: {processed} records, {errors} errors, dim={len(embeddings[-1]) if embeddings else 'N/A'}")
    return processed, errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-provider embedding generation")
    parser.add_argument("--input", required=True, help="Input JSONL file")
    parser.add_argument("--output", required=True, help="Output JSONL file")
    parser.add_argument("--backend", choices=["cohere", "cohere_light", "gemini", "ollama"], 
                      default="cohere", help="Embedding backend")
    parser.add_argument("--batch-size", type=int, default=96, help="Batch size (Cohere supports 96)")
    parser.add_argument("--dimension", type=int, default=None, help="Output dimension (Gemini only)")
    args = parser.parse_args()
    
    process_file(Path(args.input), Path(args.output), args.backend, args.batch_size, args.dimension)