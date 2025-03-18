# Elastic Search Demo

This is a project demonstrating Elastic Search search functionality, primarily implementing product description search and retrieval.

## Project Features

- Product description search with two modes:
  - Semantic similarity search (vector search)
  - Keyword match search (fuzzy search)
- Search keyword correction suggestions
- Elastic Search recommendations and hints

## Tech Stack

- Python 3.11
- Streamlit (Frontend)
- Elastic Search (Backend Service)
- Local Embedding API (Vector Embedding Service)
- uv (Package Manager)

## Project Structure

```
elastic_search_demo/
├── backend/                  # Backend API service
│   ├── main.py              # FastAPI backend service
│   ├── es_client.py         # Elastic Search client
│
├── frontend/                # Streamlit frontend
│   ├── streamlit_app.py     # Streamlit frontend app
│
├── data/                    # Data processing
│   ├── raw/                # Raw data files
│   │   └── products.json   # Sample product data
│   ├── processed/          # Processed data files
│   └── preprocessing.py    # Data preprocessing script
│
├── .env.example            # Example environment variables
├── pyproject.toml          # Project dependencies and metadata
└── README.md               # Project documentation
```

## Requirements

- Python >= 3.9
- Elastic Search (Docker deployment)
- Local Embedding API service

## Local Embedding API Setup

We recommend using LM Studio to run the embedding API locally. Here's how to set it up:

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Download the recommended model: `text-embedding-nomic-embed-text-v1.5-embedding`
3. Start the LM Studio server with the following endpoints:
```
GET http://localhost:1234/v1/models
POST http://localhost:1234/v1/chat/completions
POST http://localhost:1234/v1/completions
POST http://localhost:1234/v1/embeddings
```

4. Configure your `.env` file with:
```
# Elastic Search setting
ES_HOST=http://localhost:9200
ES_USER=elastic
ES_PASSWORD= YOUR_PASSWORD
ES_INDEX=products

# Embedding API setting
EMBEDDING_API_URL=http://localhost:1234/v1/embeddings
EMBEDDING_API_KEY=
EMBEDDING_MODEL=text-embedding-nomic-embed-text-v1.5-embedding

# API setting
API_URL=http://localhost:8000
```

## Installation

1. Clone the project
```bash
git clone [project-url]
cd elastic_search_demo
```

2. Install dependencies using uv
```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install all dependencies from pyproject.toml
uv pip install .
```

3. Configure environment variables
```bash
cp .env.example .env
# Edit .env file with necessary configuration
```

4. Run the project
```bash
# Start backend service
cd backend
python main.py

# Start frontend service
cd frontend
streamlit run streamlit_app.py
```

## Data Preprocessing

Before running the search system, you need to preprocess the data and create the Elastic Search index:

1. Place your raw data in `data/raw/products.json` with the following format:
```json
[
    {
        "product_id": "P001",
        "title": "Product Title",
        "description": "Product Description"
    }
]
```

2. Run the preprocessing script:
```bash
python data/preprocessing.py
```

This script will:
- Load raw data from `data/raw/products.json`
- Generate embeddings for product descriptions
- Create Elastic Search index with proper mappings
- Index the processed documents

The processed data will be saved in `data/processed/processed_products.json` for reference.

## Usage

1. Access the frontend interface: http://localhost:8501
2. Enter keywords in the search box
3. The system will return:
   - Semantic similarity search results
   - Keyword match search results

## Development Roadmap

- [ ] Implement user feedback mechanism
- [ ] Add retrieval evaluation functionality
- [ ] Optimize frontend interaction experience
- [ ] Add more search filtering options
- [ ] Add related product recommendations 