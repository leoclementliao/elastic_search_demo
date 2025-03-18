import streamlit as st
import httpx
import json
from typing import List, Dict, Any
import os
import sys

# Add project root directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

def search_products(query: str, size: int = 10) -> Dict[str, Any]:
    """Execute product search"""
    with httpx.Client() as client:
        response = client.post(
            f"{API_URL}/search",
            json={"query": query, "size": size}
        )
        results = response.json()
        return results

def get_suggestions(query: str, size: int = 5) -> List[str]:
    """Get search suggestions"""
    with httpx.Client() as client:
        response = client.get(
            f"{API_URL}/suggest",
            params={"query": query, "size": size}
        )
        return response.json()["suggestions"]

def display_product(product: Dict[str, Any], search_type: str):
    """Display product information"""
    st.markdown(f"### {product['title']}")
    st.markdown(f"**Search Type:** {search_type}")
    st.markdown(f"**Score:** {product.get('_score', 'N/A')}")
    st.markdown(f"**Product ID:** {product['product_id']}")
    st.markdown(f"**Description:** {product['description']}")
    st.markdown("---")

def main():
    st.title("Product Search System")
    st.markdown("""
    This is a product search system based on Elastic Search, supporting:
    - Keyword search
    - Search suggestions
    - Semantic similarity search
    """)

    # Search box
    search_query = st.text_input("Enter search keywords", "")
    
    if search_query:
        # Get search suggestions
        suggestions = get_suggestions(search_query)
        if suggestions:
            st.markdown("### Search Suggestions")
            for suggestion in suggestions:
                if st.button(suggestion):
                    search_query = suggestion
                    st.experimental_rerun()

        # Execute search
        with st.spinner("Searching..."):
            results = search_products(search_query)
            
            # Create two columns for results
            col1, col2 = st.columns(2)
            
            # Display vector search results in first column
            with col1:
                if results.get("vector_search"):
                    st.markdown("### Semantic Similarity Search Results")
                    for product in results["vector_search"]:
                        display_product(product, "Semantic Search")
            
            # Display fuzzy search results in second column
            with col2:
                if results.get("fuzzy_search"):
                    st.markdown("### Keyword Match Search Results")
                    for product in results["fuzzy_search"]:
                        display_product(product, "Keyword Search")

if __name__ == "__main__":
    main() 