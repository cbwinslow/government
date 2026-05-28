#!/usr/bin/env python3
"""
Parallel embedding generation using cbwwin RTX 3060 via Ollama API.
Processes multiple datasets concurrently for maximum throughput.
"""

import json
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import os

# Default Ollama URL
DEFAULT_OLLAMA_URL = "http://172.25.215.34:11434"
EMBEDDING_DIM = 768
MAX_WORKERS = 8
REQUEST_TIMEOUT = 60


def embed_text(text: str, ollama_url: str) -> list[float] | None:
    """Generate 768-dim embedding using cbwwin RTX 3060."""
    if not text or len(text.strip()) == 0:
        return None
    text = text[:32000]
    try:
        resp = requests.post(
            f"{ollama_url}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text},
            timeout=REQUEST_TIMEOUT
        )
        if resp.status_code == 200:
            return resp.json().get("embedding", None)
    except Exception:
        pass
    return None


def get_text_from_record(record: dict) -> str:
    """Extract text content from various record formats."""
    # Email format: body field
    if "body" in record:
        return record["body"]
    # Processed format: content field
    if "content" in record:
        return record["content"]
    # Text format
    if "text" in record:
        return record["text"]
    # Preview field (shorter)
    if "preview" in record:
        return record["preview"]
    # Subject fallback for emails
    if "subject" in record:
        text = record["subject"]
        if "preview" in record:
            text += "\n" + record["preview"]
        return text
    return ""


def process_record(args):
    """Process single record - for parallel execution."""
    i, record, ollama_url = args
    text = get_text_from_record(record)
    embedding = embed_text(text, ollama_url)
    return i, embedding


def process_file(input_file: Path, output_file: Path, ollama_url: str, text_field: str = "content"):
    """Process JSONL and add embeddings using parallel threads."""
    records = []
    
    # Load all records
    with open(input_file) as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    total = len(records)
    print(f"Loaded {total} records from {input_file}")
    
    processed = 0
    errors = 0
    results = []
    
    # Process in parallel batches
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks with ollama_url
        future_to_idx = {executor.submit(process_record, (i, r, ollama_url)): i for i, r in enumerate(records)}
        
        for future in as_completed(future_to_idx):
            idx, embedding = future.result()
            record = records[idx]
            
            if embedding:
                record["embedding"] = embedding
                record["embedding_dim"] = EMBEDDING_DIM
                results.append((idx, record))
                processed += 1
            else:
                errors += 1
            
            if processed % 100 == 0:
                print(f"  {processed}/{total} processed ({errors} errors)...")
    
    # Write results in original order
    results.sort(key=lambda x: x[0])
    with open(output_file, "w") as f:
        for _, record in results:
            f.write(json.dumps(record) + "\n")
    
    print(f"✓ Done: {processed} records, {errors} errors")
    return processed, errors


def main():
    parser = argparse.ArgumentParser(description="Parallel embedding generation")
    parser.add_argument("--input", required=True, help="Input JSONL file")
    parser.add_argument("--output", required=True, help="Output JSONL file")
    parser.add_argument("--text-field", default="content", help="Text field to embed")
    parser.add_argument("--url", default=DEFAULT_OLLAMA_URL, help="Ollama URL")
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    # Test connectivity
    try:
        resp = requests.get(f"{args.url}/api/tags", timeout=5)
        print(f"✓ Connected to Ollama at {args.url}")
    except Exception as e:
        print(f"✗ Cannot connect to {args.url}: {e}")
    
    process_file(input_path, output_path, args.url, args.text_field)


if __name__ == "__main__":
    main()