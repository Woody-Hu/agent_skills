from typing import List, Dict, Optional, Tuple
import numpy as np

try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False


class RecallEngine:
    def __init__(self, memories: List[Dict]):
        self.memories = memories
        self.bm25_index = None
        self.corpus_tokens = []
        
        if BM25_AVAILABLE and memories:
            self._init_bm25()
    
    def _init_bm25(self):
        self.corpus_tokens = []
        for mem in self.memories:
            text = self._get_searchable_text(mem)
            self.corpus_tokens.append(text.split())
        
        if self.corpus_tokens:
            self.bm25_index = BM25Okapi(self.corpus_tokens)
    
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
                reflection.get('prevention_strategy', '')
            ])
        
        return ' '.join([p for p in parts if p])
    
    def tag_match(
        self,
        query_tags: List[str],
        candidates: Optional[List[int]] = None
    ) -> Dict[int, float]:
        if candidates is None:
            candidates = list(range(len(self.memories)))
        
        scores = {}
        for idx in candidates:
            memory_tags = set(self.memories[idx].get('tags', []))
            query_tags_set = set(query_tags)
            
            if not query_tags_set:
                scores[idx] = 0.0
                continue
            
            intersection = memory_tags & query_tags_set
            scores[idx] = len(intersection) / len(query_tags_set)
        
        return scores
    
    def keyword_match(
        self,
        query_keywords: List[str],
        candidates: Optional[List[int]] = None
    ) -> Dict[int, float]:
        if candidates is None:
            candidates = list(range(len(self.memories)))
        
        scores = {}
        for idx in candidates:
            memory_keywords = set(self.memories[idx].get('keywords', []))
            query_keywords_set = set(kw.lower() for kw in query_keywords)
            memory_keywords_set = set(kw.lower() for kw in memory_keywords)
            
            if not query_keywords_set:
                scores[idx] = 0.0
                continue
            
            intersection = memory_keywords_set & query_keywords_set
            scores[idx] = len(intersection) / len(query_keywords_set)
        
        return scores
    
    def bm25_search(
        self,
        query: str,
        candidates: Optional[List[int]] = None
    ) -> Dict[int, float]:
        if not self.bm25_index:
            return {}
        
        query_tokens = query.split()
        all_scores = self.bm25_index.get_scores(query_tokens)
        
        if candidates is None:
            candidates = list(range(len(self.memories)))
        
        scores = {}
        max_score = max(all_scores) if max(all_scores) > 0 else 1.0
        
        for idx in candidates:
            if idx < len(all_scores):
                scores[idx] = all_scores[idx] / max_score
        
        return scores
    
    def rrf_fusion(
        self,
        result_sets: Dict[str, Dict[int, float]],
        weights: Optional[Dict[str, float]] = None,
        k: int = 60
    ) -> List[Tuple[int, float]]:
        if weights is None:
            weights = {key: 1.0 for key in result_sets.keys()}
        
        fusion_scores = {}
        
        for method_name, scores in result_sets.items():
            weight = weights.get(method_name, 1.0)
            
            sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            
            for rank, (doc_idx, score) in enumerate(sorted_items, 1):
                rrf_score = weight * (1.0 / (rank + k))
                
                if doc_idx in fusion_scores:
                    fusion_scores[doc_idx] += rrf_score * score
                else:
                    fusion_scores[doc_idx] = rrf_score * score
        
        sorted_results = sorted(
            fusion_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_results
    
    def hybrid_recall(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        weights: Optional[Dict[str, float]] = None,
        top_k: int = 5,
        threshold: float = 0.3
    ) -> List[Dict]:
        if not self.memories:
            return []
        
        candidates = list(range(len(self.memories)))
        
        result_sets = {}
        
        if tags:
            tag_scores = self.tag_match(tags, candidates)
            result_sets['tag'] = tag_scores
        
        if keywords:
            keyword_scores = self.keyword_match(keywords, candidates)
            result_sets['keyword'] = keyword_scores
        
        bm25_scores = self.bm25_search(query, candidates)
        if bm25_scores:
            result_sets['bm25'] = bm25_scores
        
        if not result_sets:
            return []
        
        if weights is None:
            weights = {
                'tag': 0.25,
                'keyword': 0.20,
                'bm25': 0.35,
                'vector': 0.20
            }
        
        fusion_results = self.rrf_fusion(result_sets, weights)
        
        results = []
        for idx, score in fusion_results:
            if score >= threshold:
                results.append({
                    'memory': self.memories[idx],
                    'score': score
                })
            
            if len(results) >= top_k:
                break
        
        return results
