import pytest
from unittest.mock import patch, AsyncMock
from data.embed_utils import EmbeddingClient

@pytest.fixture
def embedding_client():
    return EmbeddingClient()

@pytest.mark.asyncio
async def test_get_embedding(embedding_client):
    # Mock the API response
    mock_response = {
        "data": [{"embedding": [0.1, 0.2, 0.3]}]
    }
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.post.return_value.json.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance
        
        result = await embedding_client.get_embedding("test text")
        
        assert result == [0.1, 0.2, 0.3]
        mock_instance.post.assert_called_once()

@pytest.mark.asyncio
async def test_get_embeddings_batch(embedding_client):
    # Mock the API response
    mock_response = {
        "data": [
            {"embedding": [0.1, 0.2, 0.3]},
            {"embedding": [0.4, 0.5, 0.6]}
        ]
    }
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.post.return_value.json.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance
        
        result = await embedding_client.get_embeddings_batch(["text1", "text2"])
        
        assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_instance.post.assert_called_once()

@pytest.mark.asyncio
async def test_process_product_documents(embedding_client):
    test_documents = [
        {"description": "test product 1"},
        {"description": "test product 2"}
    ]
    
    # Mock the API response
    mock_response = {
        "data": [
            {"embedding": [0.1, 0.2, 0.3]},
            {"embedding": [0.4, 0.5, 0.6]}
        ]
    }
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.post.return_value.json.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance
        
        result = await embedding_client.process_product_documents(test_documents)
        
        assert len(result) == 2
        assert "description_embedding" in result[0]
        assert "description_embedding" in result[1]
        assert result[0]["description_embedding"] == [0.1, 0.2, 0.3]
        assert result[1]["description_embedding"] == [0.4, 0.5, 0.6] 