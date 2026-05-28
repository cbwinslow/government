#!/usr/bin/env python3
"""
Generate embeddings using local Ollama nomic-embed-text model.
Target dimension: 768
"""

import json
import os
import time
from pathlib import Path
from typing import Optional, List
import requests
import argparse

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
EMBEDDING_DIM = 768
BATCH_SIZE = 32


def embed_text(text: str) -> Optional[List[float]]:
    """Generate 768-dim embedding using local Ollama."""
    if not text or len(text.strip()) == 0:
        return None
    
    # Truncate to avoid memory issues
    text = text[:32000]
    
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text},
            timeout=120
        )
        if resp.status_code == 200:
            return resp.json().get("embedding", None)
        else:
            print(f"  Embedding error: {resp.status_code}")
            return None
    except Exception as e:
        print(f"  Embedding error: {e}")
        return None


def process_file(
    input_file: Path,
    output_file: Path,
    text_field: str = "content",
    batch_size: int = 100
):
    """Process JSONL and add embeddings."""
    processed = 0
    errors = 0
    
    with open(input_file) as f_in, open(output_file, "w") as f_out:
        for line in f_in:
            record = json.loads(line)
            
            # Extract text
            text = record.get(text_field, "")
            if not text:
                # Try other common fields
                text = record.get("text", record.get("body", record.get("message", "")))
            
            # Generate embedding
            embedding = embed_text(text)
            
            if embedding:
                record["embedding"] = embedding
                record["embedding_dim"] = EMBEDDING_DIM
                f_out.write(json.dumps(record) + "\n")
                processed += 1
            else:
                errors += 1
            
            if processed % batch_size == 0:
                print(f"  Processed {processed} samples ({errors} errors)...")
    
    print(f"  Completed: {processed} samples, {errors} errors")
    return processed, errors


def main():
    parser = argparse.ArgumentParser(description="Generate embeddings using local Ollama")
    parser.add_argument("--input", required=True, help="Input JSONL file path")
    parser.add_argument("--output", required=True, help="Output JSONL file path")
    parser.add_argument("--text-field", default="content", help="Field to embed")
    parser.add_argument("--batch-size", type=int, default=100, help="Progress report interval")
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"Generating embeddings: {input_path}")
    print(f"Output: {output_path}")
    print(f"Model: nomic-embed-text (768-dim)")
    print(f"{'='*60}\n")
    
    process_file(input_path, output_path, args.text_field, args.batch_size)


if __name__ == "__main__":
    main()