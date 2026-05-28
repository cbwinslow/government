#!/usr/bin/env python3
"""
Fast embedding using Gemini API.
Uses gemini-embedding-001 model for fast embeddings.
"""

import json
import time
from pathlib import Path
import argparse

GEMINI_API_KEY = "AIzaSyBqAWfHiUCVMROlMqwb9nc_Wptfo4-qTl4"


def embed_text_gemini(text: str) -> list[float] | None:
    """Generate embedding using Gemini API."""
    from google.genai import types
    import google.genai as genai
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    try:
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text[:9000],  # Gemini limit
            config=types.EmbedContentConfig(output_dimensionality=768)
        )
        if result.embeddings and result.embeddings[0]:
            values = result.embeddings[0].values
            return values
    except Exception as e:
        print(f"  Error: {e}")
    return None


def get_text_from_record(record: dict) -> str:
    """Extract text content from various record formats."""
    for field in ["body", "content", "text", "preview"]:
        if field in record and record[field]:
            text = record[field]
            if "subject" in record and field != "subject":
                text = f"{record.get('subject', '')}\n\n{text}"
            return text
    return ""


def process_file(input_file: Path, output_file: Path):
    """Process JSONL and add Gemini embeddings."""
    records = []
    with open(input_file, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    total = len(records)
    print(f"Loaded {total} records")
    
    processed = 0
    errors = 0
    
    with open(output_file, "w", encoding="utf-8") as f_out:
        for i, record in enumerate(records):
            text = get_text_from_record(record)
            embedding = embed_text_gemini(text)
            
            if embedding:
                record["embedding"] = embedding
                record["embedding_dim"] = len(embedding)
                f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                processed += 1
            else:
                errors += 1
            
            if (i + 1) % 100 == 0:
                print(f"  Progress: {processed}/{total} ({errors} errors)")
    
    print(f"✓ Done: {processed} records, {errors} errors")
    return processed, errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gemini embedding generation")
    parser.add_argument("--input", required=True, help="Input JSONL file")
    parser.add_argument("--output", required=True, help="Output JSONL file")
    args = parser.parse_args()
    
    process_file(Path(args.input), Path(args.output))