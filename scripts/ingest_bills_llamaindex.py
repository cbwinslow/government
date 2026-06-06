#!/usr/bin/env python3
"""LlamaIndex Hierarchical Chunker for GovInfo XML Bills."""

import os
import yaml
import logging

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    """Loads pipeline configurations."""
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config/pipelines.yaml'))
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}

def ingest_bills():
    """
    Parses GovInfo XML files using LlamaIndex HierarchicalNodeParser
    and upserts the chunks into Qdrant.
    """
    config = load_config()
    # In a full run, we would parse config['pipelines']['congress_bills'] 
    # to dynamically select the target directory.
    
    # We target the downloaded dummy bill for the test run
    target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../congress/congress-data/118'))
    if not os.path.exists(target_dir):
        logger.warning(f"Target directory {target_dir} not found. Creating dummy XML to test LlamaIndex.")
        os.makedirs(target_dir, exist_ok=True)
        dummy_xml = os.path.join(target_dir, 'BILLS-118s123is.xml')
        with open(dummy_xml, 'w', encoding='utf-8') as f:
            f.write("<bill><title>Test Bill 123</title><actions><action>Introduced</action></actions><amendments><amendment>Strike all after enacting clause</amendment></amendments></bill>")
            
    logger.info("Initializing LlamaIndex SimpleDirectoryReader...")
    documents = SimpleDirectoryReader(input_dir=target_dir, required_exts=[".xml"]).load_data()
    logger.info(f"Loaded {len(documents)} documents.")
    
    logger.info("Initializing HierarchicalNodeParser...")
    # Hierarchical parsing chunks documents into 2048 token parents, 512 token children
    node_parser = HierarchicalNodeParser.from_defaults(
        chunk_sizes=[2048, 512, 128]
    )
    
    nodes = node_parser.get_nodes_from_documents(documents)
    leaf_nodes = get_leaf_nodes(nodes)
    
    logger.info(f"Generated {len(leaf_nodes)} leaf nodes for embedding.")
    
    logger.info("Connecting to Qdrant...")
    client = QdrantClient(url="http://172.25.10.64:6333")
    vector_store = QdrantVectorStore(client=client, collection_name="congress_bills")
    
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    logger.info("Configuring Hardware Node for Embeddings...")
    embed_node = config.get("compute_nodes", {}).get("cbwdellr720", {})
    embed_url = embed_node.get("url", "http://127.0.0.1:11434")
    
    # We use BAAI/bge-m3 for dense/sparse/ColBERT multi-lingual retrieval
    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.core import Settings
    
    logger.info(f"Routing Embeddings to Ollama Node: {embed_url}")
    embed_model = OllamaEmbedding(
        model_name="bge-m3",
        base_url=embed_url,
    )
    Settings.embed_model = embed_model
    
    logger.info("Upserting nodes to Qdrant VectorStore (this triggers the hardware embedding model)...")
    index = VectorStoreIndex(
        leaf_nodes,
        storage_context=storage_context,
    )
    
    logger.info("LlamaIndex ingestion complete!")

if __name__ == "__main__":
    ingest_bills()
