import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import frontmatter

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
        self.memories_dir = self.storage_path / "memories"
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
        self.memories_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_memories(self):
        # 遍历所有记忆文件
        for root, dirs, files in os.walk(self.memories_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    try:
                        memory = self._parse_markdown_memory(file_path)
                        if memory:
                            self.memories.append(memory)
                    except Exception as e:
                        print(f"Error loading memory file {file_path}: {e}")
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
        
        # 确保corpus不为空且至少有一个非空文档
        non_empty_corpus = [doc for doc in corpus if doc]
        if non_empty_corpus:
            self.bm25_index = BM25Okapi(non_empty_corpus)
    
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
    
    def _parse_markdown_memory(self, file_path: str) -> Optional[Dict]:
        """解析Markdown记忆文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # 提取frontmatter
        memory = {
            'memory_id': post.get('memory_id'),
            'timestamp': post.get('timestamp'),
            'type': post.get('type'),
            'tags': post.get('tags', []),
            'keywords': post.get('keywords', []),
            'version': post.get('version', '1.0'),
            'file_path': file_path
        }
        
        # 解析内容
        content = post.content
        
        # 提取上下文
        context_match = self._extract_section(content, '## 上下文')
        if context_match:
            memory['context_string'] = context_match
        
        # 提取错误快照
        error_snapshot = {}
        error_match = self._extract_section(content, '### 错误信息')
        if error_match:
            for line in error_match.split('\n'):
                line = line.strip()
                if line.startswith('- 错误类型:'):
                    error_snapshot['error_type'] = line.split(':', 1)[1].strip()
                elif line.startswith('- 错误消息:'):
                    error_snapshot['error_message'] = line.split(':', 1)[1].strip()
                elif line.startswith('- 工具调用:'):
                    error_snapshot['tool_calls'] = [line.split(':', 1)[1].strip()]
                elif line.startswith('- 推理链:'):
                    error_snapshot['reasoning_chain'] = [line.split(':', 1)[1].strip()]
        if error_snapshot:
            memory['error_snapshot'] = error_snapshot
        
        # 提取成功快照
        success_snapshot = {}
        success_match = self._extract_section(content, '### 成功信息')
        if success_match:
            for line in success_match.split('\n'):
                line = line.strip()
                if line.startswith('- 成功类型:'):
                    success_snapshot['success_type'] = line.split(':', 1)[1].strip()
                elif line.startswith('- 结果:'):
                    success_snapshot['result'] = line.split(':', 1)[1].strip()
                elif line.startswith('- 工具调用:'):
                    success_snapshot['tool_calls'] = [line.split(':', 1)[1].strip()]
                elif line.startswith('- 推理链:'):
                    success_snapshot['reasoning_chain'] = [line.split(':', 1)[1].strip()]
        if success_snapshot:
            memory['success_snapshot'] = success_snapshot
        
        # 提取反思
        reflection = {}
        error_reflection_match = self._extract_section(content, '### 错误反思')
        if error_reflection_match:
            for line in error_reflection_match.split('\n'):
                line = line.strip()
                if line.startswith('- 根本原因:'):
                    reflection['root_cause'] = line.split(':', 1)[1].strip()
                elif line.startswith('- 错误描述:'):
                    reflection['what_went_wrong'] = line.split(':', 1)[1].strip()
                elif line.startswith('- 正确做法:'):
                    reflection['what_should_happen'] = line.split(':', 1)[1].strip()
                elif line.startswith('- 关键教训:'):
                    reflection['lesson_learned'] = line.split(':', 1)[1].strip()
                elif line.startswith('- 预防策略:'):
                    reflection['prevention_strategy'] = line.split(':', 1)[1].strip()
        
        success_reflection_match = self._extract_section(content, '### 成功反思')
        if success_reflection_match:
            for line in success_reflection_match.split('\n'):
                line = line.strip()
                if line.startswith('- 成功因素:'):
                    reflection['success_factors'] = line.split(':', 1)[1].strip()
                elif line.startswith('- 最佳实践:'):
                    reflection['best_practice'] = line.split(':', 1)[1].strip()
                elif line.startswith('- 关键经验:'):
                    reflection['key_experience'] = line.split(':', 1)[1].strip()
                elif line.startswith('- 推广策略:'):
                    reflection['promotion_strategy'] = line.split(':', 1)[1].strip()
        if reflection:
            memory['reflection'] = reflection
        
        # 提取元数据
        metadata = {}
        metadata_match = self._extract_section(content, '## 元数据')
        if metadata_match:
            for line in metadata_match.split('\n'):
                line = line.strip()
                if line.startswith('- 纠正状态:'):
                    metadata['success_after_correction'] = line.split(':', 1)[1].strip().lower() == 'true'
                elif line.startswith('- 纠正措施:'):
                    metadata['correction_applied'] = line.split(':', 1)[1].strip()
                elif line.startswith('- 对话轮次:'):
                    metadata['conversation_turn'] = int(line.split(':', 1)[1].strip())
        if metadata:
            memory['metadata'] = metadata
        
        return memory
    
    def _extract_section(self, content: str, section_header: str) -> Optional[str]:
        """提取Markdown章节内容"""
        import re
        pattern = rf'{section_header}\s*(.*?)(?=^##|$)'  # 匹配到下一个##或文件结束
        match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None
    
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
        """保存记忆为Markdown文件"""
        # 生成文件名
        timestamp = memory.get('timestamp', datetime.now().isoformat())
        memory_id = memory.get('memory_id', self._generate_id())
        
        # 解析时间戳以创建目录结构
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            year = str(dt.year)
            month = f'{dt.month:02d}'
        except Exception:
            # 如果时间戳格式错误，使用当前时间
            dt = datetime.now()
            year = str(dt.year)
            month = f'{dt.month:02d}'
        
        # 创建目录
        year_dir = self.memories_dir / year
        month_dir = year_dir / month
        month_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        file_name = f"{dt.strftime('%Y-%m-%d')}-{memory_id[:8]}.md"
        file_path = month_dir / file_name
        
        # 构建Markdown内容
        frontmatter_data = {
            'memory_id': memory_id,
            'timestamp': timestamp,
            'type': memory.get('type', 'unknown'),
            'tags': memory.get('tags', []),
            'keywords': memory.get('keywords', []),
            'version': memory.get('version', '1.0')
        }
        
        content = []
        content.append('# 记忆记录')
        content.append('')
        
        # 上下文
        content.append('## 上下文')
        content.append('')
        content.append(memory.get('context_string', ''))
        content.append('')
        
        # 快照
        content.append('## 快照')
        content.append('')
        
        # 错误信息
        error_snapshot = memory.get('error_snapshot', {})
        if error_snapshot:
            content.append('### 错误信息')
            content.append(f'- 错误类型: {error_snapshot.get("error_type", "")}')
            content.append(f'- 错误消息: {error_snapshot.get("error_message", "")}')
            tool_calls = error_snapshot.get('tool_calls', [])
            content.append(f'- 工具调用: {tool_calls[0] if tool_calls else ""}')
            reasoning_chain = error_snapshot.get('reasoning_chain', [])
            content.append(f'- 推理链: {reasoning_chain[0] if reasoning_chain else ""}')
            content.append('')
        
        # 成功信息
        success_snapshot = memory.get('success_snapshot', {})
        if success_snapshot:
            content.append('### 成功信息')
            content.append(f'- 成功类型: {success_snapshot.get("success_type", "")}')
            content.append(f'- 结果: {success_snapshot.get("result", "")}')
            tool_calls = success_snapshot.get('tool_calls', [])
            content.append(f'- 工具调用: {tool_calls[0] if tool_calls else ""}')
            reasoning_chain = success_snapshot.get('reasoning_chain', [])
            content.append(f'- 推理链: {reasoning_chain[0] if reasoning_chain else ""}')
            content.append('')
        
        # 反思
        content.append('## 反思')
        content.append('')
        
        # 错误反思
        reflection = memory.get('reflection', {})
        if reflection.get('root_cause') or reflection.get('what_went_wrong'):
            content.append('### 错误反思')
            content.append(f'- 根本原因: {reflection.get("root_cause", "")}')
            content.append(f'- 错误描述: {reflection.get("what_went_wrong", "")}')
            content.append(f'- 正确做法: {reflection.get("what_should_happen", "")}')
            content.append(f'- 关键教训: {reflection.get("lesson_learned", "")}')
            content.append(f'- 预防策略: {reflection.get("prevention_strategy", "")}')
            content.append('')
        
        # 成功反思
        if reflection.get('success_factors') or reflection.get('best_practice'):
            content.append('### 成功反思')
            content.append(f'- 成功因素: {reflection.get("success_factors", "")}')
            content.append(f'- 最佳实践: {reflection.get("best_practice", "")}')
            content.append(f'- 关键经验: {reflection.get("key_experience", "")}')
            content.append(f'- 推广策略: {reflection.get("promotion_strategy", "")}')
            content.append('')
        
        # 元数据
        metadata = memory.get('metadata', {})
        if metadata:
            content.append('## 元数据')
            content.append(f'- 纠正状态: {metadata.get("success_after_correction", False)}')
            content.append(f'- 纠正措施: {metadata.get("correction_applied", "")}')
            content.append(f'- 对话轮次: {metadata.get("conversation_turn", 0)}')
        
        # 创建Markdown文件
        post = frontmatter.Post('\n'.join(content), **frontmatter_data)
        
        # 写入文件
        with open(file_path, 'wb') as f:
            frontmatter.dump(post, f, encoding='utf-8')
        
        # 保存文件路径到记忆对象
        memory['file_path'] = str(file_path)
    
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
