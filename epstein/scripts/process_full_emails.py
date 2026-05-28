#!/usr/bin/env python3
"""
Process full HuggingFace datasets and generate embeddings.
Uses cbwwin RTX 3060 for fast parallel embedding.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path("epstein/data/epstein_hf")
OUTPUT_DIR = Path("epstein/output/processed_hf")


def process_to_be_emails(input_path: Path, output_dir: Path) -> int:
    """Process to-be/epstein-emails - extract content from full file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    count = 0
    with open(input_path / "train.jsonl", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            
            # Main content is in body field
            body = record.get("body", "")
            subject = record.get("subject", "")
            content = f"{subject}\n\n{body}" if body else subject
            
            if not content or len(content.strip()) < 20:
                continue
            
            out_record = {
                "document_id": record.get("doc_id", f"to-be_{count}"),
                "content": content.strip(),
                "metadata": {
                    "source_dataset": "to-be_epstein-emails",
                    "subject": subject,
                    "from_name": record.get("from_name", ""),
                    "from_email": record.get("from_email", ""),
                    "to": record.get("to", ""),
                    "date": record.get("date", ""),
                },
            }
            with open(output_dir / "processed.jsonl", "a", encoding="utf-8") as out:
                out.write(json.dumps(out_record, ensure_ascii=False) + "\n")
            count += 1
    
    return count


def process_killer_emails(input_path: Path, output_dir: Path) -> int:
    """Process KillerShoaib/Jeffrey-Epstein-Emails-From-Epstein-Files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    count = 0
    with open(input_path / "train.jsonl", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            
            # Extract body and subject
            body = record.get("body", "")
            subject = record.get("subject", "")
            preview = record.get("preview", "")
            content = f"{subject}\n\n{body}" if body else f"{subject}\n\n{preview}"
            
            if not content or len(content.strip()) < 20:
                continue
            
            out_record = {
                "document_id": record.get("doc_id", f"KillerShoaib_{count}"),
                "content": content.strip(),
                "metadata": {
                    "source_dataset": "KillerShoaib_Jeffrey-Epstein-Emails-From-Epstein-Files",
                    "subject": subject,
                    "from_name": record.get("from_name", ""),
                    "from_email": record.get("from_email", ""),
                    "to": record.get("to", ""),
                    "date": record.get("date", ""),
                },
            }
            with open(output_dir / "processed.jsonl", "a", encoding="utf-8") as out:
                out.write(json.dumps(out_record, ensure_ascii=False) + "\n")
            count += 1
    
    return count


def process_notesbymuneeb_emails(input_path: Path, output_dir: Path) -> int:
    """Process notesbymuneeb/epstein-emails - full dataset."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    count = 0
    with open(input_path / "train.jsonl", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            
            # Messages is a JSON string
            messages_str = record.get("messages", "[]")
            try:
                messages = json.loads(messages_str) if isinstance(messages_str, str) else messages_str
            except:
                messages = []
            
            # Concatenate message content
            content_parts = []
            for msg in messages:
                if isinstance(msg, dict):
                    sender = msg.get("sender", "")
                    body = msg.get("body", "")
                    if body:
                        content_parts.append(f"{sender}: {body}")
            
            content = "\n\n".join(content_parts)
            subject = record.get("subject", "")
            
            if not content or len(content.strip()) < 20:
                continue
            
            out_record = {
                "document_id": record.get("thread_id", f"notesbymuneeb_{count}"),
                "content": content.strip()[:10000],  # Truncate long threads
                "metadata": {
                    "source_dataset": "notesbymuneeb_epstein-emails",
                    "subject": subject,
                    "message_count": record.get("message_count", 0),
                    "source_file": record.get("source_file", ""),
                },
            }
            with open(output_dir / "processed.jsonl", "a", encoding="utf-8") as out:
                out.write(json.dumps(out_record, ensure_ascii=False) + "\n")
            count += 1
    
    return count


def main() -> dict[str, int]:
    """Process all email datasets for embedding."""
    results = {}
    
    # Process to-be (already full 4,272 records)
    to_be_path = DATA_DIR / "to-be_epstein-emails"
    to_be_out = OUTPUT_DIR / "emails" / "to-be_epstein-emails"
    if to_be_path.exists():
        count = process_to_be_emails(to_be_path, to_be_out)
        results["to-be_epstein-emails"] = count
        logger.info("Processed %d records from to-be_epstein-emails", count)
    
    # Process KillerShoaib (already full 10,000 records)
    killer_path = DATA_DIR / "KillerShoaib_Jeffrey-Epstein-Emails-From-Epstein-Files"
    killer_out = OUTPUT_DIR / "emails" / "KillerShoaib_Jeffrey-Epstein-Emails-From-Epstein-Files"
    if killer_path.exists():
        count = process_killer_emails(killer_path, killer_out)
        results["KillerShoaib_Jeffrey-Epstein-Emails-From-Epstein-Files"] = count
        logger.info("Processed %d records from KillerShoaib", count)
    
    # Process notesbymuneeb (currently 100 samples, need full 5,082)
    notes_path = DATA_DIR / "notesbymuneeb_epstein-emails"
    notes_out = OUTPUT_DIR / "emails" / "notesbymuneeb_epstein-emails"
    if notes_path.exists():
        count = process_notesbymuneeb_emails(notes_path, notes_out)
        results["notesbymuneeb_epstein-emails"] = count
        logger.info("Processed %d records from notesbymuneeb", count)
    
    return results


if __name__ == "__main__":
    results = main()
    print("\n=== Processing Summary ===")
    for ds, count in results.items():
        print(f"{ds}: {count} records")