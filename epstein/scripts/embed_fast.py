#!/usr/bin/env python3
"""
Fast embedding generation for Epstein datasets using local Ollama.
Processes files and saves with embeddings to output directory.
"""

import json
import requests
import time
from pathlib import Path

OLLAMA_URL = "http://localhost:11434"
EMBEDDING_DIM = 768


def embed_text(text: str) -> list[float] | None:
    """Generate 768-dim embedding using local Ollama."""
    if not text or len(text.strip()) == 0:
        return None
    text = text[:32000]
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text},
            timeout=120
        )
        if resp.status_code == 200:
            return resp.json().get("embedding", None)
        return None
    except Exception:
        return None


def process_file(input_file: Path, output_file: Path, text_field: str = "content"):
    """Process JSONL and add embeddings."""
    processed = 0
    errors = 0
    
    with open(input_file) as f_in, open(output_file, "w") as f_out:
        for line in f_in:
            record = json.loads(line)
            text = record.get(text_field, record.get("text", record.get("body", "")))
            
            embedding = embed_text(text)
            
            if embedding:
                record["embedding"] = embedding
                record["embedding_dim"] = EMBEDDING_DIM
                f_out.write(json.dumps(record) + "\n")
                processed += 1
            else:
                errors += 1
            
            if processed % 100 == 0:
                print(f"  {processed} processed ({errors} errors)...")
    
    print(f"Done: {processed} records, {errors} errors")
    return processed, errors


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: embed_fast.py <input.jsonl> <output.jsonl> [text_field]")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    text_field = sys.argv[3] if len(sys.argv) > 3 else "content"
    
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    process_file(input_path, output_path, text_field)