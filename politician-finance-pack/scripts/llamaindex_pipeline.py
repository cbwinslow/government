import os
from typing import List, Dict, Any

from llama_index.core import Document, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline


def build_documents(rows: List[Dict[str, Any]]) -> List[Document]:
    docs = []
    for row in rows:
        text = row.get("text", "")
        metadata = {k: v for k, v in row.items() if k != "text"}
        docs.append(Document(text=text, metadata=metadata))
    return docs


def build_pipeline():
    return IngestionPipeline(transformations=[SentenceSplitter(chunk_size=1024, chunk_overlap=100)])


if __name__ == "__main__":
    sample = [{"text": "Sample politician disclosure text", "person_id": 1, "document_type": "ptr"}]
    docs = build_documents(sample)
    pipeline = build_pipeline()
    nodes = pipeline.run(documents=docs)
    print({"nodes": len(nodes), "status": "ok"})
