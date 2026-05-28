#!/usr/bin/env python3
"""
Efficient Gemini embedding with proper rate limit handling.
"""
import json
import time
import os
import sys

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBqAWfHiUCVMROlMqwb9nc_Wptfo4-qTl4")

import google.genai as genai
from google.genai import types

EMBEDDING_DIM = 768

def main():
    if len(sys.argv) < 3:
        print("Usage: script.py <input.jsonl> <output.jsonl>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Load existing embedded IDs
    done_ids = set()
    if os.path.exists(output_file):
        with open(output_file) as f:
            for line in f:
                if line.strip():
                    rec = json.loads(line)
                    did = rec.get("document_id", rec.get("doc_id", ""))
                    done_ids.add(did)
        print(f"Already embedded: {len(done_ids)}")
    
    # Load all records
    records = []
    with open(input_file) as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    print(f"Total records: {len(records)}")
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Process remaining
    to_embed = [r for r in records if r.get("document_id", r.get("doc_id", "")) not in done_ids]
    print(f"To embed: {len(to_embed)}")
    
    embedded = 0
    errors = 0
    
    # Open in append mode
    with open(output_file, "a") as f_out:
        for i, rec in enumerate(to_embed):
            doc_id = rec.get("document_id", rec.get("doc_id", ""))
            
            # Extract text
            text = ""
            for field in ["content", "body", "text", "preview"]:
                if field in rec and rec[field]:
                    text = rec[field]
                    if "subject" in rec and field != "subject":
                        text = f"{rec.get('subject', '')}\n\n{text}"
                    break
            
            try:
                result = client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=text[:9000],
                    config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIM)
                )
                if result.embeddings and result.embeddings[0]:
                    rec["embedding"] = result.embeddings[0].values
                    rec["embedding_dim"] = EMBEDDING_DIM
                    f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    f_out.flush()
                    embedded += 1
                else:
                    errors += 1
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "quota" in err_str.lower():
                    # Extract wait time
                    import re
                    match = re.search(r'retry in ([\d.]+)s', err_str)
                    wait = float(match.group(1)) + 5 if match else 60
                    print(f"Quota hit, waiting {wait}s...", file=sys.stderr)
                    time.sleep(wait)
                    # Try once more
                    try:
                        result = client.models.embed_content(
                            model="gemini-embedding-001",
                            contents=text[:9000],
                            config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIM)
                        )
                        if result.embeddings and result.embeddings[0]:
                            rec["embedding"] = result.embeddings[0].values
                            rec["embedding_dim"] = EMBEDDING_DIM
                            f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                            f_out.flush()
                            embedded += 1
                        else:
                            errors += 1
                    except:
                        errors += 1
                else:
                    print(f"Error: {e}", file=sys.stderr)
                    errors += 1
            
            # Progress every 50
            if (i + 1) % 50 == 0:
                print(f"Progress: {embedded} done, {errors} errors", file=sys.stderr)
            
            # Rate limit: ~100 req/min, so 0.65s delay
            time.sleep(0.65)
    
    print(f"Done: {embedded} records, {errors} errors", file=sys.stderr)

if __name__ == "__main__":
    main()