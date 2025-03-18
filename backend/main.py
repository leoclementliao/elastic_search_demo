from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import sys
import os

# Add project root directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from backend.es_client import ESClient
from data.embed_utils import EmbeddingClient

app = FastAPI(title="Elastic Search Demo API")
es_client = ESClient()
embedding_client = EmbeddingClient()

class SearchQuery(BaseModel):
    query: str
    size: Optional[int] = 10

class ProductDocument(BaseModel):
    product_id: str
    title: str
    description: str
    description_embedding: Optional[List[float]] = None

@app.get("/")
async def root():
    return {"message": "Welcome to Elastic Search Demo API"}

@app.post("/search")
async def search(query: SearchQuery):
    """Execute search"""
    try:
        # Get vector representation of query text
        query_vector = await embedding_client.get_embedding(query.query)
        
        # Execute vector search
        vector_results = es_client.vector_search(query_vector, query.size)
        
        # Execute fuzzy search
        fuzzy_results = es_client.fuzzy_search(query.query, size=query.size)
        
        return {
            "vector_search": vector_results,
            "fuzzy_search": fuzzy_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/suggest")
async def suggest(query: str, size: int = 5):
    """Get search suggestions"""
    try:
        suggestions = es_client.suggest(query, "description", size)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/products")
async def create_product(product: ProductDocument):
    """Create new product"""
    try:
        # Generate embedding if not provided
        if not product.description_embedding:
            product.description_embedding = await embedding_client.get_embedding(product.description)
        
        # Create document
        success = es_client.update_document(product.product_id, product.model_dump())
        if success:
            return {"message": "Product created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create product")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get product information"""
    product = es_client.get_document(product_id)
    if product:
        return product
    else:
        raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """Delete product"""
    success = es_client.delete_document(product_id)
    if success:
        return {"message": "Product deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Product not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 