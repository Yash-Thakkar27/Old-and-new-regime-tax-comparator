# rag_index.py
"""
Vector indexing and retrieval for legal documents and tax snippets.
Uses FAISS for local vector storage with provider-agnostic embedding wrapper.
"""
import os
import json
import logging
from typing import List, Dict, Optional, Tuple
import numpy as np

try:
    import faiss
except ImportError:
    faiss = None

from config import (
    EMBEDDING_MODEL, 
    LLM_MODEL, 
    GEMINI_API_KEY,
    INDEX_PATH, 
    INDEX_METADATA_PATH, 
    LEGAL_DOCS_PATH,
    TOP_K_SNIPPETS,
    SIMILARITY_THRESHOLD
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Embedding & LLM Wrapper Functions (Provider-Agnostic Placeholders)
# ============================================================================

import google.generativeai as genai

# Configure Gemini at module level
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_embedding(text: str) -> Optional[List[float]]:
    print(f"[EMBEDDING] Requesting embedding for: {text[:50]}...")
    
    if not GEMINI_API_KEY:
        print("[ERROR] No API key!")
        return None
    
    try:
        print("[EMBEDDING] Calling Gemini...")
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        print(f"[EMBEDDING] ✓ Success! Dimension: {len(result['embedding'])}")
        return result['embedding']
    except Exception as e:
        print(f"[EMBEDDING] ✗ Failed: {e}")
        return None
# def get_embedding(text: str) -> Optional[List[float]]:
#     """
#     Get embedding vector for text using Gemini embedding model.
#     """
#     print(f"\n[RAG] get_embedding called for text: {text[:50]}...")

#     if not EMINI_API_KEY:
#         logger.warning("EMINI_API_KEY not set, cannot generate embeddings")
#         return None
    
#     try:
#         print("[RAG] Calling Gemini API for embedding...")
#         result = genai.embed_content(
#             model="models/text-embedding-004",
#             content=text,
#             task_type="retrieval_document"
#         )
#         print(f"[RAG SUCCESS] Embedding generated, dimension: {len(result['embedding'])}")
#         return result['embedding']
        
#     except Exception as e:
#         print(f"[RAG ERROR] Failed to get embedding: {e}")
#         logger.error(f"Error getting embedding from Gemini: {e}")
#         return None
    
#     try:
#         # Use Gemini's embedding model
#         result = genai.embed_content(
#             model="models/text-embedding-004",  # or "models/embedding-001"
#             content=text,
#             task_type="retrieval_document"
#         )
#         return result['embedding']
        
#     except Exception as e:
#         logger.error(f"Error getting embedding from Gemini: {e}")
#         return None


def call_llm(prompt: str) -> Optional[str]:
    """
    Call Gemini LLM with prompt.
    """
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set, cannot call LLM")
        return None
    
    try:
        # Use Gemini's generative model
        model = genai.GenerativeModel(LLM_MODEL)
        response = model.generate_content(
            prompt,
            generation_config={
                'max_output_tokens': 100,
                'temperature': 0.3,
            }
        )
        return response.text
        
    except Exception as e:
        logger.error(f"Error calling Gemini LLM: {e}")
        return None
# def get_embedding(text: str) -> Optional[List[float]]:
#     """
#     Get embedding vector for text using {{EMBEDDING_MODEL}}.
    
#     Replace this implementation with your provider's SDK.
#     Example providers: OpenAI, Anthropic, Cohere, local models, etc.
    
#     Args:
#         text: Input text to embed
        
#     Returns:
#         List of floats representing the embedding, or None on error
#     """
#     if not GEMINI_API_KEY:
#         logger.warning("GEMINI_API_KEY not set, cannot generate embeddings")
#         return None
    
#     try:
#         # PLACEHOLDER: Replace with actual API call
#         # Example for OpenAI-compatible API:
#         # import openai
#         # openai.api_key = EMINI_API_KEY
#         # response = openai.Embedding.create(
#         #     input=text,
#         #     model=EMBEDDING_MODEL
#         # )
#         # return response['data'][0]['embedding']
        
#         # For demo purposes, return a random embedding
#         # REMOVE THIS IN PRODUCTION
#         logger.warning("Using dummy embeddings - configure real API")
#         np.random.seed(hash(text) % (2**32))
#         return np.random.rand(384).tolist()  # Typical embedding dimension
        
#     except Exception as e:
#         logger.error(f"Error getting embedding: {e}")
#         return None


# def call_llm(prompt: str) -> Optional[str]:
#     """
#     Call LLM with prompt using {{LLM_MODEL}}.
    
#     Replace this implementation with your provider's SDK.
    
#     Args:
#         prompt: The prompt to send to the LLM
        
#     Returns:
#         Generated text response, or None on error
#     """
#     if not EMINI_API_KEY:
#         logger.warning("EMINI_API_KEY not set, cannot call LLM")
#         return None
    
#     try:
#         # PLACEHOLDER: Replace with actual API call
#         # Example for OpenAI-compatible API:
#         # import openai
#         # openai.api_key = EMINI_API_KEY
#         # response = openai.ChatCompletion.create(
#         #     model=LLM_MODEL,
#         #     messages=[{"role": "user", "content": prompt}],
#         #     max_tokens=100,
#         #     temperature=0.3
#         # )
#         # return response.choices[0].message.content
        
#         # For demo purposes, return empty
#         logger.warning("Using dummy LLM - configure real API")
#         return None
        
#     except Exception as e:
#         logger.error(f"Error calling LLM: {e}")
#         return None


# ============================================================================
# Vector Index Management
# ============================================================================

class LegalVectorIndex:
    """Manages FAISS vector index for legal documents and snippets."""
    
    def __init__(self, index_path: str, metadata_path: str):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = None
        self.metadata = []
        self.dimension = 384  # Default dimension, will be updated
        
    def build_index(self, documents: List[Dict[str, str]]) -> bool:
        print(f"\n[INDEX] Building index with {len(documents)} documents...")
        """
        Build FAISS index from documents.
        
        Args:
            documents: List of dicts with keys 'key', 'text', 'source'
            
        Returns:
            True if successful, False otherwise
        """
        if faiss is None:
            logger.error("FAISS not installed. Install with: pip install faiss-cpu")
            return False
        
        if not documents:
            logger.warning("No documents to index")
            return False
        
        try:
            # Generate embeddings
            embeddings = []
            valid_metadata = []
            
            for doc in documents:
                embedding = get_embedding(doc['text'])
                if embedding is not None:
                    embeddings.append(embedding)
                    valid_metadata.append({
                        'key': doc['key'],
                        'text': doc['text'],
                        'source': doc['source']
                    })
            
            if not embeddings:
                logger.error("No valid embeddings generated")
                return False
            
            # Create FAISS index
            embeddings_array = np.array(embeddings).astype('float32')
            self.dimension = embeddings_array.shape[1]
            
            # Use L2 distance (can be changed to inner product for cosine similarity)
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(embeddings_array)
            self.metadata = valid_metadata
            
            # Save index and metadata
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            faiss.write_index(self.index, self.index_path)
            
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            
            logger.info(f"Built index with {len(self.metadata)} documents")

            print(f"[INDEX] ✓ Built successfully with {len(self.metadata)} docs")
            print(f"[INDEX] Saved to: {self.index_path}\n")
            return True
            
        except Exception as e:
            logger.error(f"Error building index: {e}")
            return False
    
    def load_index(self) -> bool:
        """Load existing index from disk."""
        if faiss is None:
            logger.error("FAISS not installed")
            return False
        
        try:
            if not os.path.exists(self.index_path) or not os.path.exists(self.metadata_path):
                return False
            
            self.index = faiss.read_index(self.index_path)
            
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
            
            logger.info(f"Loaded index with {len(self.metadata)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            
        Returns:
            List of dicts with keys 'key', 'text', 'source', 'score'
        """
        if self.index is None:
            logger.warning("Index not loaded")
            return []
        
        try:
            # Get query embedding
            query_embedding = get_embedding(query)
            if query_embedding is None:
                return []
            
            # Search
            query_array = np.array([query_embedding]).astype('float32')
            distances, indices = self.index.search(query_array, min(top_k, len(self.metadata)))
            
            # Format results
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < len(self.metadata):
                    # Convert L2 distance to similarity score (0-1 range)
                    similarity = 1.0 / (1.0 + float(dist))
                    
                    if similarity >= SIMILARITY_THRESHOLD:
                        result = self.metadata[idx].copy()
                        result['score'] = round(similarity, 4)
                        results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching index: {e}")
            return []


# ============================================================================
# Document Loading and Index Building
# ============================================================================

def load_legal_documents(docs_path: str) -> List[Dict[str, str]]:
    """
    Load legal documents from local folder.
    
    Args:
        docs_path: Path to folder containing .txt and .md files
        
    Returns:
        List of document dicts with keys 'key', 'text', 'source'
    """
    documents = []
    
    if not os.path.exists(docs_path):
        logger.info(f"Legal docs path {docs_path} does not exist, skipping")
        return documents
    
    try:
        for filename in os.listdir(docs_path):
            if filename.endswith(('.txt', '.md')):
                filepath = os.path.join(docs_path, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        documents.append({
                            'key': filename,
                            'text': content,
                            'source': filename
                        })
        
        logger.info(f"Loaded {len(documents)} documents from {docs_path}")
        
    except Exception as e:
        logger.error(f"Error loading legal documents: {e}")
    
    return documents


def build_index_from_snippets_and_docs(
    snippets_dict: Dict[str, str],
    docs_path: str = LEGAL_DOCS_PATH
) -> LegalVectorIndex:
    """
    Build or load vector index from snippets and legal documents.
    
    Args:
        snippets_dict: Dictionary of snippet_key -> snippet_text
        docs_path: Path to legal documents folder
        
    Returns:
        LegalVectorIndex instance (may be empty if build fails)
    """
    vector_index = LegalVectorIndex(INDEX_PATH, INDEX_METADATA_PATH)
    
    # Try to load existing index
    if vector_index.load_index():
        logger.info("Using existing index")
        return vector_index
    
    # Build new index
    logger.info("Building new index...")
    
    # Prepare documents from snippets
    documents = []
    for key, text in snippets_dict.items():
        documents.append({
            'key': f"snippet:{key}",
            'text': text,
            'source': '_RAG_SNIPPETS'
        })
    
    # Add documents from legal_docs folder
    legal_docs = load_legal_documents(docs_path)
    documents.extend(legal_docs)
    
    # Build index
    if documents:
        vector_index.build_index(documents)
    else:
        logger.warning("No documents available for indexing")
    
    return vector_index


# ============================================================================
# RAG Retrieval Function
# ============================================================================

def retrieve_legal_snippets(
    profile: Dict,
    vector_index: LegalVectorIndex,
    top_k: int = TOP_K_SNIPPETS
) -> Dict[str, Dict]:
    print(f"[RETRIEVE] Searching for top {top_k} snippets...")
    """
    Retrieve relevant legal snippets based on user profile.
    
    Args:
        profile: User tax profile dictionary
        vector_index: Initialized vector index
        top_k: Number of snippets to retrieve
        
    Returns:
        Dictionary mapping snippet keys to snippet info dicts
    """
    if vector_index.index is None:
        logger.warning("Vector index not available for retrieval")
        return {}
    
    # Build query from profile
    query_parts = []
    
    if profile.get("investments_80c", 0) > 0:
        query_parts.append("80C deduction investments PPF ELSS")
    if profile.get("insurance_80d", 0) > 0:
        query_parts.append("80D medical insurance premium")
    if profile.get("home_loan_interest", 0) > 0:
        query_parts.append("home loan interest section 24")
    if profile.get("hra_exempt", 0) > 0:
        query_parts.append("HRA exemption")
    if profile.get("lta_exempt", 0) > 0:
        query_parts.append("LTA leave travel allowance")
    if profile.get("ltcg_equity", 0) > 0:
        query_parts.append("equity LTCG long term capital gains")
    if profile.get("stcg_equity", 0) > 0:
        query_parts.append("equity STCG short term capital gains")
    
    query_parts.append("standard deduction salary income tax")
    query_parts.append("rebate surcharge cess")
    
    query = " ".join(query_parts)
    
    # Retrieve
    results = vector_index.search(query, top_k=top_k)
    
    # Format as dict
    snippets_dict = {}
    for result in results:
        key = result['key'].replace('snippet:', '')
        snippets_dict[key] = {
            'text': result['text'],
            'score': result['score'],
            'source': result['source']
        }
    print(f"[RETRIEVE] ✓ Found {len(snippets_dict)} relevant snippets")
    return snippets_dict


def augment_explanation_with_llm(
    original_explanation: str,
    retrieved_snippets: Dict[str, Dict],
    profile: Dict
) -> str:
    """
    Optionally augment explanation with LLM-generated note based on retrieved docs.
    
    Args:
        original_explanation: Original explanation text
        retrieved_snippets: Retrieved legal snippets
        profile: User tax profile
        
    Returns:
        Augmented explanation (or original if LLM fails)
    """
    if not retrieved_snippets:
        return original_explanation
    
    try:
        # Build prompt
        snippets_text = "\n".join([
            f"- {info['text']}" 
            for info in list(retrieved_snippets.values())[:3]
        ])
        
        prompt = f"""Based on these tax law snippets:
{snippets_text}

Original explanation: {original_explanation}

Generate a single short sentence (max 20 words) that adds a relevant legal reference to support the explanation. 
Start with "RAG note:" and do not contradict the original explanation."""
        
        llm_response = call_llm(prompt)
        
        if llm_response and llm_response.strip():
            augmented = f"{original_explanation} ({llm_response.strip()})"
            return augmented
        
    except Exception as e:
        logger.error(f"Error augmenting explanation with LLM: {e}")
    
    return original_explanation