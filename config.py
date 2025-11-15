# config.py
import os
from dotenv import load_dotenv

# RAG Configuration
USE_RAG = True  # Set to False to use only _RAG_SNIPPETS fallback

# API Keys - Replace with your actual keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # {{GEMINI_API_KEY}}

# Model Configuration
EMBEDDING_MODEL = "text-embedding-3-small"  # {{EMBEDDING_MODEL}}
LLM_MODEL = "o3-mini"  # {{LLM_MODEL}}

# Vector Index Configuration
INDEX_PATH = "./indexes/legal_index.faiss"
INDEX_METADATA_PATH = "./indexes/legal_metadata.json"
LEGAL_DOCS_PATH = "./legal_docs/"

# Retrieval Configuration
TOP_K_SNIPPETS = 5
SIMILARITY_THRESHOLD = 0.3

# Model Configuration
EMBEDDING_MODEL = "models/text-embedding-004"  # Gemini embedding model
LLM_MODEL = "gemini-pro"  # Gemini LLM model