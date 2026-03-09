from typing import List, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class EmbeddingEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.dimension = None
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self._load_model()
    
    def _load_model(self):
        try:
            self.model = SentenceTransformer(self.model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
        except Exception as e:
            print(f"Warning: Failed to load embedding model: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        return SENTENCE_TRANSFORMERS_AVAILABLE and self.model is not None
    
    def encode(self, text: str) -> List[float]:
        if not self.is_available():
            return []
        
        try:
            vector = self.model.encode(text)
            return vector.tolist()
        except Exception as e:
            print(f"Warning: Failed to encode text: {e}")
            return []
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        if not self.is_available():
            return [[] for _ in texts]
        
        try:
            vectors = self.model.encode(texts)
            return vectors.tolist()
        except Exception as e:
            print(f"Warning: Failed to encode batch: {e}")
            return [[] for _ in texts]
    
    def get_dimension(self) -> Optional[int]:
        return self.dimension
    
    def compute_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2:
            return 0.0
        
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(v1, v2) / (norm1 * norm2))
    
    def build_index(self, vectors: List[List[float]]):
        if not self.is_available():
            return None
        
        try:
            import faiss
            dimension = len(vectors[0])
            index = faiss.IndexFlatL2(dimension)
            index.add(np.array(vectors, dtype=np.float32))
            return index
        except Exception as e:
            print(f"Warning: Failed to build FAISS index: {e}")
            return None
    
    def search(
        self,
        query_vector: List[float],
        index,
        k: int = 5
    ) -> List[tuple]:
        if index is None or not query_vector:
            return []
        
        try:
            query = np.array([query_vector], dtype=np.float32)
            distances, indices = index.search(query, k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx >= 0:
                    similarity = 1.0 / (1.0 + distances[0][i])
                    results.append((int(idx), float(similarity)))
            
            return results
        except Exception as e:
            print(f"Warning: Failed to search index: {e}")
            return []
