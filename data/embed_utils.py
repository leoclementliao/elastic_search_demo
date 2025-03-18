from typing import List, Dict, Any
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

class EmbeddingClient:
    def __init__(self):
        self.api_url = os.getenv("EMBEDDING_API_URL", "http://localhost:1234/v1/embeddings")
        self.api_key = os.getenv("EMBEDDING_API_KEY", "")
        self.model = os.getenv("EMBEDDING_MODEL", "local-model")

    async def get_embedding(self, text: str) -> List[float]:
        """Get vector representation of a single text"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                json={
                    "input": text,
                    "model": self.model
                }
            )
            await response.raise_for_status()
            response_data = await response.json()
            return response_data["data"][0]["embedding"]

    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get vector representations of multiple texts"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                json={
                    "input": texts,
                    "model": self.model
                }
            )
            await response.raise_for_status()
            response_data = await response.json()
            return [item["embedding"] for item in response_data["data"]]

    async def process_product_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process product documents and add vector representations"""
        texts = [doc["description"] for doc in documents]
        embeddings = await self.get_embeddings_batch(texts)
        
        for doc, embedding in zip(documents, embeddings):
            doc["description_embedding"] = embedding
        return documents 