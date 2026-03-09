# 科研智能体记忆系统

## 简介

本skill为科研智能体提供错误记忆记录和动态召回能力，帮助智能体从错误中学习并持续改进。

## 目录结构

```
research-agent-memory/
├── SKILL.md              # 技能定义文件
├── README.md             # 本文件
├── scripts/              # 核心脚本
│   ├── __init__.py
│   ├── memory_system.py  # 核心记忆系统
│   ├── recall.py         # 召回引擎
│   ├── embedding.py      # 向量化模块
│   └── cli.py            # 命令行接口
└── memory_store/         # 记忆存储目录（自动创建）
```

## 安装依赖

### 基本依赖

```bash
pip install sentence-transformers faiss-cpu rank-bm25
```



## 快速开始

### 1. 记录记忆

#### 记录错误记忆

```bash
# 记录工具使用错误
python scripts/cli.py record --type tool_error \
    --tags "error:tool_error,tool:python_interpreter,severity:high,domain:data_processing,stage:execution" \
    --keywords "pandas,memory_error,read_csv,chunksize" \
    --context "任务：分析100万条科研数据，使用pandas进行数据清洗。当前步骤：读取CSV文件并转换为DataFrame。"

# 使用反射文件记录
python scripts/cli.py record --type tool_error \
    --tags "error:tool_error,tool:python_interpreter" \
    --keywords "pandas,memory_error" \
    --context "任务：分析科研数据" \
    --reflection-file reflection.json
```

#### 记录成功记忆

```bash
# 记录工具使用成功
python scripts/cli.py record --type tool_success \
    --tags "success:tool_success,tool:python_interpreter,domain:data_processing,stage:execution" \
    --keywords "pandas,chunksize,data_analysis,success" \
    --context "任务：分析100万条科研数据，使用pandas进行数据清洗。当前步骤：使用chunksize分块读取CSV文件。"

# 记录用户主动引入的成功经验
python scripts/cli.py record --type user_experience \
    --tags "success:user_experience,domain:data_processing,stage:execution" \
    --keywords "pandas,chunksize,best_practice,user_experience" \
    --context "用户主动分享：使用chunksize分块处理大文件的经验，避免内存溢出。"

# 使用反射文件记录成功经验
python scripts/cli.py record --type task_completed \
    --tags "success:task_completed,domain:data_processing,stage:execution" \
    --keywords "pandas,data_analysis,completed" \
    --context "任务：成功完成100万条数据的分析" \
    --reflection-file success_reflection.json
```

### 2. 召回相关记忆

```bash
# 按关键词召回
python scripts/cli.py recall --query "pandas读取大文件内存溢出" \
    --top-k 3

# 按标签过滤
python scripts/cli.py recall --query "内存溢出" \
    --tags "tool:python_interpreter,error:tool_error" \
    --top-k 5

# 混合过滤
python scripts/cli.py recall --query "数据处理错误" \
    --tags "domain:data_processing" \
    --keywords "pandas,memory" \
    --top-k 3
```

### 3. 上下文增强

```bash
# 增强提示词
python scripts/cli.py augment --task "分析科研数据集" \
    --prompt-file prompt.txt \
    --output augmented_prompt.txt
```

### 4. 查看统计信息

```bash
# 查看记忆统计
python scripts/cli.py stats

# 列出所有记忆
python scripts/cli.py list --limit 20
```

## Python API 使用

```python
from scripts.memory_system import ResearchAgentMemory

# 初始化记忆系统
memory_system = ResearchAgentMemory("./memory_store")

# 记录记忆
memory_id = memory_system.record({
    "type": "tool_error",
    "tags": [
        "error:tool_error",
        "tool:python_interpreter",
        "severity:high",
        "domain:data_processing",
        "stage:execution"
    ],
    "keywords": ["pandas", "memory_error", "read_csv", "chunksize"],
    "context_string": "任务：分析100万条科研数据...",
    "error_snapshot": {
        "error_type": "MemoryError",
        "error_message": "Unable to allocate 2.5 GiB for an array..."
    },
    "reflection": {
        "root_cause": "尝试一次性加载超过可用内存的大数据集",
        "what_went_wrong": "直接使用pd.read_csv()读取大文件",
        "what_should_happen": "使用chunksize参数分块读取",
        "lesson_learned": "处理大数据集时需要考虑内存限制",
        "prevention_strategy": "读取前检查文件大小，设置chunksize参数"
    },
    "metadata": {
        "success_after_correction": True,
        "correction_applied": "使用chunksize=10000分块读取"
    }
})

# 召回记忆
related_memories = memory_system.recall(
    query="pandas处理大文件",
    tags=["tool:python_interpreter"],
    top_k=3
)

# 上下文增强
augmented_prompt = memory_system.augment_context(
    task_description="分析科研数据集",
    current_prompt="请分析以下数据..."
)
```

## 存储结构

记忆以 JSON 格式存储在 `memory_store/memories.jsonl` 中，每行一个记忆。索引文件存储在 `memory_store/index/` 目录中。

## 混合召回策略

系统采用四层混合召回策略：

1. **标签匹配** (25%) - 基于标签的精确匹配
2. **关键词匹配** (20%) - 基于关键词的精确匹配
3. **BM25语义召回** (35%) - 基于文本语义的BM25评分
4. **向量相似度** (20%) - 基于Sentence-BERT的语义向量

## 向量化方案

默认使用 **Sentence-BERT (all-MiniLM-L6-v2)** 模型：
- 模型大小：约22MB
- 向量维度：384维
- 推理速度：快
- 语义理解：强

## 注意事项

1. **依赖安装**：首次使用前请安装所有依赖
2. **权限**：确保有写入 `memory_store` 目录的权限
3. **性能**：对于大量记忆，召回速度可能会降低
4. **隐私**：记忆中可能包含敏感信息，请适当处理

## 版本历史

- v1.0.0: 初始版本，支持基本的记忆记录和混合召回
