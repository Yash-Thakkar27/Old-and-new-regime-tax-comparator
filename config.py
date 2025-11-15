# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# # RAG Configuration
# USE_RAG = False  # Set to False to use only _RAG_SNIPPETS fallback

# # API Keys - Replace with your actual keys
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # {{GEMINI_API_KEY}}

# # Model Configuration
# EMBEDDING_MODEL = "text-embedding-3-small"  # {{EMBEDDING_MODEL}}
# LLM_MODEL = "o3-mini"  # {{LLM_MODEL}}

# # Vector Index Configuration
# INDEX_PATH = "./indexes/legal_index.faiss"
# INDEX_METADATA_PATH = "./indexes/legal_metadata.json"
# LEGAL_DOCS_PATH = "./legal_docs/"

# # Retrieval Configuration
# TOP_K_SNIPPETS = 5
# SIMILARITY_THRESHOLD = 0.3

# # Model Configuration
# EMBEDDING_MODEL = "models/text-embedding-004"  # Gemini embedding model
# LLM_MODEL = "gemini-pro"  # Gemini LLM model

# # At the END of config.py file
# print("\n" + "="*80)
# print("RAG CONFIG LOADED")
# print("="*80)
# print(f"USE_RAG: {USE_RAG}")
# print(f"API Key Set: {'YES' if GEMINI_API_KEY else 'NO'}")
# print(f"API Key Length: {len(GEMINI_API_KEY)}")
# print("="*80 + "\n")

# config.py
USE_RAG = True

# FAISS index files (paths used by code)
INDEX_PATH = "./index/faiss.index"
INDEX_METADATA_PATH = "./index/metadata.json"
LEGAL_DOCS_PATH = "./legal_docs/"

# RAG retrieval parameters
TOP_K_SNIPPETS = 15
SIMILARITY_THRESHOLD = 0.01

# Embedding/LLM keys — set these either here (not secure) or as environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")   # used by google.generativeai in the code
EMINI_API_KEY = GEMINI_API_KEY  # some functions check EMINI_API_KEY — make them point to same key

# Models (optional)
EMBEDDING_MODEL = "models/text-embedding-004"
LLM_MODEL = "gemini-2.0-flash"
