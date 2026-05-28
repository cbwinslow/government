#!/usr/bin/env python3
"""
Sequential embedding with checkpointing for Epstein datasets.
Uses local Ollama (nomic-embed-text) for 768-dim embeddings.
Robust to interruptions - saves progress and can resume.
"""

import json
import requests
import time
from pathlib import Path
from typing import Optional
import argparse

OLLAMA_URL = "http://localhost:11434"
EMBEDDING_DIM = 768
REQUEST_TIMEOUT = 60
BATCH_SIZE = 50


def embed_text(text: str, model: str = "nomic-embed-text") -> Optional[list[float]]:
    """Generate embedding using Ollama API."""
    if not text or len(text.strip()) == 0:
        return None
    text = text[:32000]
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": model, "prompt": text},
            timeout=REQUEST_TIMEOUT
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("embedding", None)
    except Exception as e:
        print(f"  Error: {e}")
    return None


def get_text_from_record(record: dict) -> str:
    """Extract text content from various record formats."""
    for field in ["body", "content", "text", "preview"]:
        if field in record and record[field]:
            text = record[field]
            if "subject" in record and text and field != "subject":
                text = f"{record.get('subject', '')}\n\n{text}"
            return text
    return ""


def embed_dataset(
    input_file: Path,
    output_file: Path,
    checkpoint_file: Optional[Path] = None,
    model: str = "nomic-embed-text",
):
    """Generate embeddings with checkpointing."""
    
    # Load all records
    records = []
    with open(input_file, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    total = len(records)
    print(f"Loaded {total} records from {input_file}")
    
    # Load checkpoint if exists
    processed_indices = set()
    if checkpoint_file and checkpoint_file.exists():
        with open(checkpoint_file) as f:
            processed_indices = set(json.load(f))
        print(f"Resuming from checkpoint: {len(processed_indices)} records already processed")
    
    processed = 0
    errors = 0
    
    # Process records
    with open(output_file, "a", encoding="utf-8") as f_out:
        for i, record in enumerate(records):
            if i in processed_indices:
                processed += 1
                continue
            
            text = get_text_from_record(record)
            embedding = embed_text(text, model)
            
            if embedding and len(embedding) == EMBEDDING_DIM:
                record["embedding"] = embedding
                record["embedding_dim"] = EMBEDDING_DIM
                f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                f_out.flush()
                processed_indices.add(i)
                processed += 1
            else:
                errors += 1
            
            # Save checkpoint periodically
            if i % BATCH_SIZE == 0 and checkpoint_file:
                with open(checkpoint_file, "w") as f:
                    json.dump(list(processed_indices), f)
            
            if (i + 1) % 20 == 0:
                print(f"  Progress: {processed}/{total} done ({errors} errors)")
    
    # Final checkpoint
    if checkpoint_file:
        with open(checkpoint_file, "w") as f:
            json.dump(list(processed_indices), f)
    
    print(f"✓ Complete: {processed} records, {errors} errors")
    return processed, errors


def main():
    parser = argparse.ArgumentParser(description="Sequential embedding with checkpointing")
    parser.add_argument("--input", required=True, help="Input JSONL file")
    parser.add_argument("--output", required=True, help="Output JSONL file")
    parser.add_argument("--checkpoint", help="Checkpoint file for resume")
    parser.add_argument("--model", default="nomic-embed-text", help="Ollama model")
    args = parser.parse_args()
    
    embed_dataset(
        Path(args.input),
        Path(args.output),
        Path(args.checkpoint) if args.checkpoint else None,
        args.model
    )


if __name__ == "__main__":
    main()