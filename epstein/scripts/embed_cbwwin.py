#!/usr/bin/env python3
"""
Use Ollama on cbwwin (RTX 3060) for fast embedding generation.
"""

import json
import requests
import concurrent.futures
import time
from pathlib import Path
import argparse

# cbwwin has RTX 3060 for faster embedding
OLLAMA_URL = "http://172.25.215.34:11434"
EMBEDDING_DIM = 768


def embed_text(text: str) -> list[float] | None:
    """Generate 768-dim embedding using cbwwin RTX 3060."""
    if not text or len(text.strip()) == 0:
        return None
    text = text[:32000]
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text},
            timeout=180
        )
        if resp.status_code == 200:
            return resp.json().get("embedding", None)
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None


def process_file(input_file: Path, output_file: Path, text_field: str = "content"):
    """Process JSONL and add embeddings."""
    processed = 0
    errors = 0
    
    with open(input_file) as f_in, open(output_file, "w") as f_out:
        for i, line in enumerate(f_in):
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
            
            if (i + 1) % 50 == 0:
                print(f"  Record {i+1}: {processed} embeddings, {errors} errors")
    
    print(f"Done: {processed} records, {errors} errors")
    return processed, errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--text-field", default="content")
    args = parser.parse_args()
    
    process_file(Path(args.input), Path(args.output), args.text_field)