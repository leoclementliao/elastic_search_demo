import json
import os
import sys
from typing import List, Dict, Any

# Add project root directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from backend.es_client import ESClient
from data.embed_utils import EmbeddingClient

def load_raw_data(file_path: str) -> List[Dict[str, Any]]:
    """Load raw data"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def process_data(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process data and add vector representations"""
    embedding_client = EmbeddingClient()
    processed_docs = embedding_client.process_product_documents(documents)
    
    # Save processed data
    processed_dir = os.path.join(current_dir, "processed")
    os.makedirs(processed_dir, exist_ok=True)
    processed_file_path = os.path.join(processed_dir, "processed_products.json")
    
    with open(processed_file_path, 'w', encoding='utf-8') as f:
        json.dump(processed_docs, f, ensure_ascii=False, indent=4)
    
    return processed_docs

def create_index_mapping() -> Dict[str, Any]:
    """Create index mapping"""
    return {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "product_id": {"type": "keyword"},
                "title": {"type": "text"},
                "description": {
                    "type": "text",
                    "analyzer": "standard"
                },
                "description_embedding": {
                    "type": "dense_vector",
                    "dims": 768,  # dimension of the embedding model
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }
    }

def main():
    # Initialize client
    es_client = ESClient()
    
    # Create index
    mapping = create_index_mapping()
    es_client.create_index(mapping)
    
    # Load raw data
    raw_data_path = os.path.join(current_dir, "raw", "products.json")
    if not os.path.exists(raw_data_path):
        print(f"Raw data file does not exist: {raw_data_path}")
        return
    
    documents = load_raw_data(raw_data_path)
    
    # Process data
    processed_documents = process_data(documents)
    
    # Bulk import data
    success = es_client.bulk_index_documents(processed_documents)
    if success:
        print("Data import successful!")
    else:
        print("Data import failed!")

if __name__ == "__main__":
    main() 