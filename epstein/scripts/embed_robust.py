#!/usr/bin/env python3
"""
Robust embedding with rate limit handling.
Supports both Gemini (fast) and Ollama (slow) backends.
"""

import json
import time
from pathlib import Path
import argparse
import os

# Try to import google-genai
try:
    import google.genai as genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

EMBEDDING_DIM = 768
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBqAWfHiUCVMROlMqwb9nc_Wptfo4-qTl4")

# Global client for efficiency
_CLIENT = None

def get_client():
    global _CLIENT
    if _CLIENT is None and HAS_GENAI:
        _CLIENT = genai.Client(api_key=GEMINI_API_KEY)
    return _CLIENT

def embed_gemini(text: str, max_retries: int = 3) -> list[float] | None:
    """Generate embedding using Gemini API with rate limit handling."""
    if not HAS_GENAI:
        return None
    
    client = get_client()
    for attempt in range(max_retries):
        try:
            result = client.models.embed_content(
                model="gemini-embedding-001",
                contents=text[:9000],
                config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIM)
            )
            if result.embeddings and result.embeddings[0]:
                return result.embeddings[0].values
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate" in error_str.lower():
                wait = 60 * (attempt + 1)
                print(f"  Rate limited (attempt {attempt+1}), waiting {wait}s...")
                time.sleep(wait)
                continue
            print(f"  Gemini error: {e}")
    return None


def embed_ollama(text: str) -> list[float] | None:
    """Generate embedding using Ollama (local fallback)."""
    import requests
    try:
        resp = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text[:32000]},
            timeout=60
        )
        if resp.status_code == 200:
            return resp.json().get("embedding", None)
    except Exception as e:
        print(f"  Ollama error: {e}")
    return None


def get_text_from_record(record: dict) -> str:
    """Extract text content from record."""
    # Handle KillerShoaib format: body field with subject
    if "body" in record and record["body"]:
        text = record["body"]
        if "subject" in record:
            text = f"{record.get('subject', '')}\n\n{record.get('preview', '')}\n\n{text}"
        return text
    # Handle notesbymuneeb format: content field with subject
    for field in ["body", "content", "text", "preview"]:
        if field in record and record[field]:
            text = record[field]
            if field != "subject" and "subject" in record:
                text = f"{record.get('subject', '')}\n\n{text}"
            return text
    return ""


def process_with_backend(input_file: Path, output_file: Path, backend: str = "gemini", delay: float = 0.6):
    """Process with rate limit aware backend."""
    records = []
    with open(input_file, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    total = len(records)
    print(f"Loaded {total} records, using {backend} backend")
    
    processed = 0
    errors = 0
    
    # Skip already processed - use document_id + message_order as unique key
    done_keys = set()
    if output_file.exists():
        with open(output_file) as f:
            for line in f:
                rec = json.loads(line)
                # Handle both doc_id and document_id formats
                doc_id = rec.get("document_id", rec.get("doc_id", ""))
                msg_order = rec.get("metadata", {}).get("message_order", rec.get("message_order", 0))
                done_keys.add(f"{doc_id}_{msg_order}")
        print(f"Already processed: {len(done_keys)} records")
    
    with open(output_file, "a", encoding="utf-8") as f_out:
        for i, record in enumerate(records):
            doc_id = record.get("document_id", "")
            msg_order = record.get("metadata", {}).get("message_order", record.get("message_order", 0))
            key = f"{doc_id}_{msg_order}"
            if key in done_keys:
                continue
            
            text = get_text_from_record(record)
            
            if backend == "gemini":
                embedding = embed_gemini(text)
            else:
                embedding = embed_ollama(text)
            
            if embedding and len(embedding) == EMBEDDING_DIM:
                record["embedding"] = embedding
                record["embedding_dim"] = EMBEDDING_DIM
                f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                f_out.flush()
                processed += 1
            else:
                errors += 1
            
            # Rate limit delay
            if backend == "gemini":
                time.sleep(delay)
            
            if (i + 1) % 100 == 0:
                print(f"  Progress: {processed} done, {errors} errors")
    
    print(f"✓ Done: {processed} records, {errors} errors")
    return processed, errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Robust embedding generation")
    parser.add_argument("--input", required=True, help="Input JSONL file")
    parser.add_argument("--output", required=True, help="Output JSONL file")
    parser.add_argument("--backend", choices=["gemini", "ollama"], default="gemini")
    parser.add_argument("--delay", type=float, default=0.65, help="Delay between requests (seconds)")
    args = parser.parse_args()
    
    process_with_backend(Path(args.input), Path(args.output), args.backend, args.delay)