from typing import List
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_MODEL = None
    EMBEDDING_DIMENSION = 384
    
    def initialize_embedding_model(model_name: str = "all-MiniLM-L6-v2"):
        global EMBEDDING_MODEL, EMBEDDING_DIMENSION
        if EMBEDDING_MODEL is None:
            print(f"Loading Sentence Transformer model: {model_name}...")
            EMBEDDING_MODEL = SentenceTransformer(model_name)
            EMBEDDING_DIMENSION = EMBEDDING_MODEL.get_sentence_embedding_dimension()
            print(f"Model loaded! Embedding dimension: {EMBEDDING_DIMENSION}")
        return EMBEDDING_MODEL
    
except ImportError:
    print("Warning: sentence-transformers not available. Using fallback embeddings.")
    EMBEDDING_MODEL = None
    EMBEDDING_DIMENSION = 384
    
    def initialize_embedding_model(model_name: str = "all-MiniLM-L6-v2"):
        print("Sentence Transformers not available. Using random embeddings for development.")
        return None


def generate_embedding(text: str) -> List[float]:
    if EMBEDDING_MODEL is None:
        return [np.random.random() for _ in range(EMBEDDING_DIMENSION)]
    
    try:
        embedding = EMBEDDING_MODEL.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return [0.0] * EMBEDDING_DIMENSION


def generate_query_embedding(query: str) -> List[float]:
    if EMBEDDING_MODEL is None:
        return [np.random.random() for _ in range(EMBEDDING_DIMENSION)]
    
    try:
        embedding = EMBEDDING_MODEL.encode(query, convert_to_tensor=False)
        return embedding.tolist()
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        return [0.0] * EMBEDDING_DIMENSION


def generate_batch_embeddings(texts: List[str]) -> List[List[float]]:
    if EMBEDDING_MODEL is None:
        return [[np.random.random() for _ in range(EMBEDDING_DIMENSION)] for _ in texts]
    
    try:
        embeddings = EMBEDDING_MODEL.encode(
            texts,
            convert_to_tensor=False,
            show_progress_bar=True,
            batch_size=32
        )
        return [emb.tolist() for emb in embeddings]
    except Exception as e:
        print(f"Error generating batch embeddings: {e}")
        return [[0.0] * EMBEDDING_DIMENSION for _ in texts]
