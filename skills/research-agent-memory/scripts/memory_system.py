import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False


class ResearchAgentMemory:
    def __init__(self, storage_path: str = "./memory_store"):
        self.storage_path = Path(storage_path)
        self.memories_path = self.storage_path / "memories.jsonl"
        self.index_path = self.storage_path / "index"
        
        self.memories: List[Dict] = []
        self.bm25_index = None
        self.vector_index = None
        self.tag_index: Dict[str, List[int]] = {}
        self.embedding_model = None
        
        self._init_storage()
        self._load_memories()
        self._init_indexes()
    
    def _init_storage(self):
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        if not self.memories_path.exists():
            self.memories_path.touch()
    
    def _load_memories(self):
        if not self.memories_path.exists() or self.memories_path.stat().st_size == 0:
            return
            
        with open(self.memories_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        self.memories.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    
    def _init_indexes(self):
        self._build_tag_index()
        if BM25_AVAILABLE:
            self._build_bm25_index()
        if FAISS_AVAILABLE and SENTENCE_TRANSFORMERS_AVAILABLE:
            self._build_vector_index()
    
    def _build_tag_index(self):
        self.tag_index = {}
        for idx, memory in enumerate(self.memories):
            tags = memory.get('tags', [])
            for tag in tags:
                if tag not in self.tag_index:
                    self.tag_index[tag] = []
                self.tag_index[tag].append(idx)
    
    def _build_bm25_index(self):
        if not self.memories:
            return
            
        corpus = []
        for mem in self.memories:
            text = self._get_searchable_text(mem)
            corpus.append(text.split())
        
        if corpus:
            self.bm25_index = BM25Okapi(corpus)
    
    def _build_vector_index(self):
        if not self.memories:
            return
            
        vectors = []
        valid_indices = []
        
        for idx, mem in enumerate(self.memories):
            vec = mem.get('embedding_vector', [])
            if vec and len(vec) > 0:
                vectors.append(vec)
                valid_indices.append(idx)
        
        if not vectors:
            return
            
        dimension = len(vectors[0])
        self.vector_index = faiss.IndexFlatL2(dimension)
        self.vector_index.add(np.array(vectors, dtype=np.float32))
        self.vector_valid_indices = valid_indices
    
    def _get_searchable_text(self, memory: Dict) -> str:
        parts = [
            memory.get('context_string', ''),
            memory.get('type', ''),
            ' '.join(memory.get('tags', [])),
            ' '.join(memory.get('keywords', [])),
        ]
        
        reflection = memory.get('reflection', {})
        if reflection:
            parts.extend([
                reflection.get('root_cause', ''),
                reflection.get('lesson_learned', ''),
                reflection.get('prevention_strategy', ''),
                reflection.get('success_factors', ''),
                reflection.get('best_practice', ''),
                reflection.get('key_experience', ''),
                reflection.get('promotion_strategy', '')
            ])
        
        success_snapshot = memory.get('success_snapshot', {})
        if success_snapshot:
            parts.extend([
                success_snapshot.get('success_type', ''),
                success_snapshot.get('result', '')
            ])
        
        error_snapshot = memory.get('error_snapshot', {})
        if error_snapshot:
            parts.extend([
                error_snapshot.get('error_type', ''),
                error_snapshot.get('error_message', '')
            ])
        
        return ' '.join([p for p in parts if p])
    
    def _generate_id(self) -> str:
        return str(uuid.uuid4())
    
    def record(self, memory_data: Dict) -> str:
        memory_id = self._generate_id()
        memory_data['memory_id'] = memory_id
        memory_data['timestamp'] = datetime.now().isoformat()
        memory_data['version'] = '1.0'
        
        if 'embedding_vector' not in memory_data and SENTENCE_TRANSFORMERS_AVAILABLE:
            memory_data['embedding_vector'] = self._generate_embedding(memory_data)
        
        self.memories.append(memory_data)
        self._save_memory(memory_data)
        self._update_indexes(memory_data)
        
        return memory_id
    
    def _generate_embedding(self, memory: Dict) -> List[float]:
        if self.embedding_model is None:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception:
                return []
        
        text = self._get_searchable_text(memory)
        try:
            vector = self.embedding_model.encode(text)
            return vector.tolist()
        except Exception:
            return []
    
    def _save_memory(self, memory: Dict):
        with open(self.memories_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(memory, ensure_ascii=False) + '\n')
    
    def _update_indexes(self, memory: Dict):
        idx = len(self.memories) - 1
        
        tags = memory.get('tags', [])
        for tag in tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            self.tag_index[tag].append(idx)
        
        if BM25_AVAILABLE:
            self._build_bm25_index()
        
        if FAISS_AVAILABLE and SENTENCE_TRANSFORMERS_AVAILABLE:
            vec = memory.get('embedding_vector', [])
            if vec:
                if self.vector_index is None:
                    dimension = len(vec)
                    self.vector_index = faiss.IndexFlatL2(dimension)
                self.vector_index.add(np.array([vec], dtype=np.float32))
    
    def recall(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        top_k: int = 5,
        threshold: float = 0.3
    ) -> List[Dict]:
        if not self.memories:
            return []
        
        candidates = set(range(len(self.memories)))
        
        if tags:
            tag_candidates = self._tag_search(tags)
            candidates &= tag_candidates
        
        if keywords:
            keyword_candidates = self._keyword_search(keywords)
            candidates &= keyword_candidates
        
        if not candidates:
            candidates = set(range(len(self.memories)))
        
        candidates = list(candidates)
        
        scores = {idx: 0.0 for idx in candidates}
        
        if BM25_AVAILABLE and self.bm25_index:
            bm25_scores = self._bm25_search(query, candidates)
            for idx, score in bm25_scores.items():
                scores[idx] += score * 0.35
        
        if keywords:
            keyword_scores = self._keyword_match_scores(query, candidates)
            for idx, score in keyword_scores.items():
                scores[idx] += score * 0.20
        
        if tags:
            tag_scores = self._tag_match_scores(query, tags, candidates)
            for idx, score in tag_scores.items():
                scores[idx] += score * 0.25
        
        if FAISS_AVAILABLE and self.vector_index and SENTENCE_TRANSFORMERS_AVAILABLE:
            vector_scores = self._vector_search(query, candidates)
            for idx, score in vector_scores.items():
                scores[idx] += score * 0.20
        
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, score in sorted_scores[:top_k]:
            if score >= threshold:
                results.append(self.memories[idx])
        
        return results
    
    def _tag_search(self, tags: List[str]) -> set:
        result = set()
        for tag in tags:
            if tag in self.tag_index:
                result.update(self.tag_index[tag])
        return result
    
    def _keyword_search(self, keywords: List[str]) -> set:
        result = set()
        for idx, memory in enumerate(self.memories):
            memory_keywords = set(memory.get('keywords', []))
            for kw in keywords:
                if kw.lower() in [k.lower() for k in memory_keywords]:
                    result.add(idx)
                    break
        return result
    
    def _keyword_match_scores(self, query: str, candidates: List[int]) -> Dict[int, float]:
        scores = {}
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for idx in candidates:
            memory_keywords = self.memories[idx].get('keywords', [])
            match_count = 0
            for kw in memory_keywords:
                if kw.lower() in query_words:
                    match_count += 1
            if memory_keywords:
                scores[idx] = match_count / len(memory_keywords)
            else:
                scores[idx] = 0.0
        
        return scores
    
    def _tag_match_scores(self, query: str, tags: List[str], candidates: List[int]) -> Dict[int, float]:
        scores = {}
        for idx in candidates:
            memory_tags = set(self.memories[idx].get('tags', []))
            match_count = sum(1 for tag in tags if tag in memory_tags)
            if tags:
                scores[idx] = match_count / len(tags)
            else:
                scores[idx] = 0.0
        
        return scores
    
    def _bm25_search(self, query: str, candidates: List[int]) -> Dict[int, float]:
        if not self.bm25_index:
            return {}
        
        query_words = query.split()
        scores = self.bm25_index.get_scores(query_words)
        
        result = {}
        max_score = max(scores) if max(scores) > 0 else 1.0
        for idx in candidates:
            if idx < len(scores):
                result[idx] = scores[idx] / max_score
        
        return result
    
    def _vector_search(self, query: str, candidates: List[int]) -> Dict[int, float]:
        if not self.vector_index or not self.embedding_model:
            return {}
        
        try:
            query_vector = self.embedding_model.encode(query)
            query_vector = np.array([query_vector], dtype=np.float32)
            
            distances, indices = self.vector_index.search(query_vector, len(candidates))
            
            result = {}
            for i, idx in enumerate(indices[0]):
                if idx >= 0 and idx in candidates:
                    similarity = 1.0 / (1.0 + distances[0][i])
                    result[idx] = similarity
            
            return result
        except Exception:
            return {}
    
    def augment_context(
        self,
        task_description: str,
        current_prompt: str,
        top_k: int = 3,
        threshold: float = 0.5
    ) -> str:
        memories = self.recall(
            query=task_description,
            top_k=top_k,
            threshold=threshold
        )
        
        if not memories:
            return current_prompt
        
        context_hint = "\n\n## 相关历史经验\n"
        for i, mem in enumerate(memories, 1):
            context_hint += f"\n### 经验 {i}\n"
            context_hint += f"- 类型: {mem.get('type', 'unknown')}\n"
            context_hint += f"- 标签: {', '.join(mem.get('tags', []))}\n"
            
            reflection = mem.get('reflection', {})
            if reflection.get('lesson_learned'):
                context_hint += f"- 关键教训: {reflection['lesson_learned']}\n"
            if reflection.get('prevention_strategy'):
                context_hint += f"- 预防策略: {reflection['prevention_strategy']}\n"
        
        return current_prompt + context_hint
    
    def get_memory(self, memory_id: str) -> Optional[Dict]:
        for memory in self.memories:
            if memory.get('memory_id') == memory_id:
                return memory
        return None
    
    def list_memories(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        return self.memories[offset:offset + limit]
    
    def delete_memory(self, memory_id: str) -> bool:
        for i, memory in enumerate(self.memories):
            if memory.get('memory_id') == memory_id:
                self.memories.pop(i)
                self._rebuild_all_indexes()
                return True
        return False
    
    def _rebuild_all_indexes(self):
        self.tag_index = {}
        for idx, memory in enumerate(self.memories):
            tags = memory.get('tags', [])
            for tag in tags:
                if tag not in self.tag_index:
                    self.tag_index[tag] = []
                self.tag_index[tag].append(idx)
        
        if BM25_AVAILABLE:
            self._build_bm25_index()
        
        if FAISS_AVAILABLE and SENTENCE_TRANSFORMERS_AVAILABLE:
            self._build_vector_index()
    
    def get_stats(self) -> Dict[str, Any]:
        tag_counts = {}
        for memory in self.memories:
            for tag in memory.get('tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return {
            "total_memories": len(self.memories),
            "unique_tags": len(self.tag_index),
            "tag_distribution": tag_counts,
            "bm25_available": BM25_AVAILABLE,
            "vector_available": FAISS_AVAILABLE and SENTENCE_TRANSFORMERS_AVAILABLE
        }
