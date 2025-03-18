from typing import List, Dict, Any, Optional
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import os
from dotenv import load_dotenv

load_dotenv()

class ESClient:
    def __init__(self):
        # Get authentication credentials from environment variables
        es_user = os.getenv("ES_USER", "elastic")
        es_password = os.getenv("ES_PASSWORD", "")
        es_host = os.getenv("ES_HOST", "http://localhost:9200")
        
        # Initialize Elasticsearch client with authentication
        self.es = Elasticsearch(
            hosts=[es_host],
            basic_auth=(es_user, es_password),
            verify_certs=False  # For development only
        )
        self.index_name = os.getenv("ES_INDEX", "products")

    def create_index(self, mapping: Dict[str, Any]) -> bool:
        """Create index"""
        try:
            if not self.es.indices.exists(index=self.index_name):
                # Create index with settings
                self.es.indices.create(
                    index=self.index_name,
                    settings=mapping.get("settings", {}),
                    mappings=mapping.get("mappings", {})
                )
                return True
            return False
        except Exception as e:
            print(f"Error creating index: {str(e)}")
            return False

    def bulk_index_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Bulk index documents"""
        try:
            actions = [
                {
                    "_index": self.index_name,
                    "_id": doc["product_id"],
                    "_source": doc
                }
                for doc in documents
            ]
            success, failed = bulk(self.es, actions, refresh=True)
            if failed:
                print(f"Failed to index {len(failed)} documents")
                for item in failed:
                    print(f"Error details: {item}")
            return len(failed) == 0
        except Exception as e:
            print(f"Error bulk indexing documents: {str(e)}")
            return False

    def search(self, query: Dict[str, Any], size: int = 10) -> List[Dict[str, Any]]:
        """Execute search"""
        try:
            response = self.es.search(
                index=self.index_name,
                query=query,
                size=size
            )
            return [
                {
                    **hit["_source"],
                    "_score": hit["_score"]
                }
                for hit in response["hits"]["hits"]
            ]
        except Exception as e:
            print(f"Error executing search: {str(e)}")
            return []

    def suggest(self, text: str, field: str, size: int = 5) -> List[str]:
        """Get search suggestions"""
        try:
            response = self.es.search(
                index=self.index_name,
                body={
                    "suggest": {
                        "suggestions": {
                            "prefix": text,
                            "completion": {
                                "field": field,
                                "size": size
                            }
                        }
                    }
                }
            )
            return [option["text"] for option in response["suggest"]["suggestions"][0]["options"]]
        except Exception as e:
            print(f"Error getting suggestions: {str(e)}")
            return []

    def vector_search(self, vector: List[float], size: int = 10) -> List[Dict[str, Any]]:
        """Vector search"""
        try:
            query = {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'description_embedding') + 1.0",
                        "params": {"query_vector": vector}
                    }
                }
            }
            return self.search(query, size)
        except Exception as e:
            print(f"Error executing vector search: {str(e)}")
            return []

    def fuzzy_search(self, text: str, field: str = "description", size: int = 10) -> List[Dict[str, Any]]:
        """Fuzzy search"""
        try:
            query = {
                "multi_match": {
                    "query": text,
                    "fields": ["title^2", "description"],
                    "fuzziness": "AUTO",
                    "type": "best_fields"
                }
            }
            return self.search(query, size)
        except Exception as e:
            print(f"Error executing fuzzy search: {str(e)}")
            return []

    def get_document(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get single document"""
        try:
            response = self.es.get(index=self.index_name, id=product_id)
            return response["_source"]
        except Exception as e:
            print(f"Error getting document: {str(e)}")
            return None

    def update_document(self, product_id: str, doc: Dict[str, Any]) -> bool:
        """Update document"""
        try:
            self.es.update(index=self.index_name, id=product_id, doc=doc)
            return True
        except Exception as e:
            print(f"Error updating document: {str(e)}")
            return False

    def delete_document(self, product_id: str) -> bool:
        """Delete document"""
        try:
            self.es.delete(index=self.index_name, id=product_id)
            return True
        except Exception as e:
            print(f"Error deleting document: {str(e)}")
            return False 