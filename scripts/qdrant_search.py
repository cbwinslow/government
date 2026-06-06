#!/usr/bin/env python3
"""Search utility for Qdrant congress bills collection via Haystack RAG."""

import sys
import os

# Add src to path so we can import opendiscourse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from opendiscourse.core.haystack_retriever import CongressRetriever

def main():
    """Interactive semantic search using Haystack Pipeline."""
    if len(sys.argv) < 2:
        print("Usage: python qdrant_search.py <query>")
        print("Example: python qdrant_search.py 'Truman death resolution'")
        return

    query = " ".join(sys.argv[1:])
    print(f"Searching for: {query}")
    print("-" * 50)

    retriever = CongressRetriever()
    results = retriever.search(query, top_k=5)

    if not results:
        print("No results found.")
        return

    for i, doc in enumerate(results, 1):
        # Haystack Documents store payload in meta
        meta = doc.meta
        print(f"\n{i}. {meta.get('bill_id', 'Unknown Bill ID')}")
        title = meta.get('official_title', 'No Title')
        print(f"   Title: {title[:100]}...")
        print(f"   Score: {doc.score:.4f}")
        print(f"   Snippet: {doc.content[:150]}...")

if __name__ == "__main__":
    main()
