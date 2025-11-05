from typing import List
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_MODEL = None
    EMBEDDING_DIMENSION = 768  # Expected dimension
    
    def initialize_embedding_model(model_name: str = "all-mpnet-base-v2"):
        global EMBEDDING_MODEL, EMBEDDING_DIMENSION
        if EMBEDDING_MODEL is None:
            print(f"🔄 Loading Sentence Transformer model: {model_name}...")
            EMBEDDING_MODEL = SentenceTransformer(model_name)
            EMBEDDING_DIMENSION = EMBEDDING_MODEL.get_sentence_embedding_dimension()
            
            # Verify embedding dimension
            print(f"✅ Model loaded successfully!")
            print(f"📊 Embedding dimension: {EMBEDDING_DIMENSION}")
            
            # Test embedding generation
            test_text = "test embedding"
            test_embedding = EMBEDDING_MODEL.encode(test_text, convert_to_tensor=False)
            actual_dim = len(test_embedding)
            
            if actual_dim != EMBEDDING_DIMENSION:
                print(f"⚠️  Warning: Dimension mismatch! Expected {EMBEDDING_DIMENSION}, got {actual_dim}")
            else:
                print(f"✅ Embedding dimension verified: {actual_dim} dimensions")
            
            # Additional model info
            print(f"📦 Model: {model_name}")
            print(f"🔢 Max sequence length: {EMBEDDING_MODEL.max_seq_length}")
            
        return EMBEDDING_MODEL
    
except ImportError:
    print("⚠️  Warning: sentence-transformers not available. Using fallback embeddings.")
    EMBEDDING_MODEL = None
    EMBEDDING_DIMENSION = 768
    
    def initialize_embedding_model(model_name: str = "all-mpnet-base-v2"):
        print("⚠️  Sentence Transformers not available. Using random embeddings for development.")
        print(f"📊 Fallback embedding dimension: {EMBEDDING_DIMENSION}")
        return None


def generate_embedding(text: str) -> List[float]:
    """Generate embedding for a single text."""
    if EMBEDDING_MODEL is None:
        # Fallback: random embeddings
        return [float(np.random.random()) for _ in range(EMBEDDING_DIMENSION)]
    
    try:
        embedding = EMBEDDING_MODEL.encode(text, convert_to_tensor=False)
        result = embedding.tolist()
        
        # Verify dimension
        if len(result) != EMBEDDING_DIMENSION:
            print(f"⚠️  Warning: Generated embedding has {len(result)} dimensions, expected {EMBEDDING_DIMENSION}")
        
        return result
    except Exception as e:
        print(f"❌ Error generating embedding: {e}")
        return [0.0] * EMBEDDING_DIMENSION


def generate_query_embedding(query: str) -> List[float]:
    """Generate embedding for a query (same as generate_embedding but explicit name)."""
    if EMBEDDING_MODEL is None:
        return [float(np.random.random()) for _ in range(EMBEDDING_DIMENSION)]
    
    try:
        embedding = EMBEDDING_MODEL.encode(query, convert_to_tensor=False)
        result = embedding.tolist()
        
        # Verify dimension
        if len(result) != EMBEDDING_DIMENSION:
            print(f"⚠️  Warning: Query embedding has {len(result)} dimensions, expected {EMBEDDING_DIMENSION}")
        
        return result
    except Exception as e:
        print(f"❌ Error generating query embedding: {e}")
        return [0.0] * EMBEDDING_DIMENSION


def generate_batch_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts efficiently."""
    if EMBEDDING_MODEL is None:
        return [[float(np.random.random()) for _ in range(EMBEDDING_DIMENSION)] for _ in texts]
    
    try:
        print(f"🔄 Generating embeddings for {len(texts)} texts...")
        embeddings = EMBEDDING_MODEL.encode(
            texts,
            convert_to_tensor=False,
            show_progress_bar=True,
            batch_size=32
        )
        
        result = [emb.tolist() for emb in embeddings]
        
        # Verify dimensions
        for i, emb in enumerate(result):
            if len(emb) != EMBEDDING_DIMENSION:
                print(f"⚠️  Warning: Embedding {i} has {len(emb)} dimensions, expected {EMBEDDING_DIMENSION}")
        
        print(f"✅ Successfully generated {len(result)} embeddings with {EMBEDDING_DIMENSION} dimensions each")
        return result
        
    except Exception as e:
        print(f"❌ Error generating batch embeddings: {e}")
        return [[0.0] * EMBEDDING_DIMENSION for _ in texts]


def get_embedding_dimension() -> int:
    """Get the current embedding dimension."""
    return EMBEDDING_DIMENSION


def verify_embedding_compatibility(embedding: List[float]) -> bool:
    """Verify if an embedding has the correct dimension."""
    if len(embedding) != EMBEDDING_DIMENSION:
        print(f"⚠️  Embedding dimension mismatch: {len(embedding)} vs expected {EMBEDDING_DIMENSION}")
        return False
    return True