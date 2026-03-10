---
name: research-agent-memory
description: "科研智能体记忆系统。记录错误、反思和经验，支持动态混合召回。Invoke when agent makes mistakes, receives user feedback, or needs to recall past experiences."
---

# 科研智能体记忆系统

本skill为科研智能体提供错误记忆记录和动态召回能力，帮助智能体从错误中学习并持续改进。

## 触发条件

**必须触发场景：**

1. **用户明确要求记录** - 用户提及"记下这个"、"这个做错了"、"记住这个"、"记录下来"等说法
2. **工具使用错误** - 调用工具时返回错误、参数错误、工具不可用等
3. **推理错误** - 思路错误、逻辑错误、假设错误、方法选择不当
4. **工作流程错误** - 执行顺序错误、步骤遗漏、任务理解偏差
5. **用户反馈** - 用户指出问题、纠正错误、提供反馈
6. **任务失败** - 任务无法完成、超时、结果不符合预期
7. **成功执行** - 用户主动引入的成功经验、工具调用成功、推理正确、工作流程顺畅、任务完成
8. **需要召回历史经验** - 开始新任务前、遇到困难时、用户询问相关问题

## 记忆数据结构

### Markdown 记忆文件格式

每个记忆以单独的Markdown文件存储，文件名格式：`{timestamp}-{memory_id}.md`

```markdown
---
memory_id: "uuid"
timestamp: "ISO8601时间戳"
type: "记忆类型"
tags: ["标签1", "标签2"]
keywords: ["关键词1", "关键词2"]
version: "1.0"
---

# 记忆记录

## 上下文

[完整上下文描述]

## 快照

### 错误信息（错误记忆）
- 错误类型: [错误类型]
- 错误消息: [错误消息]
- 工具调用: [工具调用记录]
- 推理链: [推理链]

### 成功信息（成功记忆）
- 成功类型: [成功类型]
- 结果: [成功结果]
- 工具调用: [工具调用记录]
- 推理链: [推理链]

## 反思

### 错误反思
- 根本原因: [根本原因分析]
- 错误描述: [错误描述]
- 正确做法: [正确做法]
- 关键教训: [关键教训]
- 预防策略: [预防策略]

### 成功反思
- 成功因素: [成功因素]
- 最佳实践: [最佳实践]
- 关键经验: [关键经验]
- 推广策略: [推广策略]

## 元数据

- 纠正状态: [是否已纠正]
- 纠正措施: [应用的纠正措施]
- 对话轮次: [对话轮次]
```

### 示例记忆文件

```markdown
---
memory_id: "550e8400-e29b-41d4-a716-446655440000"
timestamp: "2026-03-09T10:00:00Z"
type: "tool_error"
tags: ["error:tool_error", "tool:python_interpreter", "domain:data_processing"]
keywords: ["pandas", "memory_error", "read_csv", "chunksize"]
version: "1.0"
---

# 记忆记录

## 上下文

任务：分析100万条科研数据，使用pandas进行数据清洗。当前步骤：读取CSV文件并转换为DataFrame。

## 快照

### 错误信息
- 错误类型: MemoryError
- 错误消息: Unable to allocate 2.5 GiB for an array with shape (1000000, 250)
- 工具调用: pd.read_csv('large_data.csv')
- 推理链: 需要读取CSV文件 → 使用pandas → 直接读取全部数据

## 反思

### 错误反思
- 根本原因: 尝试一次性加载超过可用内存的大数据集到内存中
- 错误描述: 直接使用pd.read_csv('large_data.csv')尝试将整个大文件加载到内存，未考虑文件大小和内存限制
- 正确做法: 在读取大文件前应先检查文件大小，使用chunksize参数分块读取，或仅加载需要的列，使用dtype优化内存
- 关键教训: 处理大数据集时必须考虑内存限制，不能一次性加载全部数据
- 预防策略: 建立大文件处理检查机制：1)读取前检查文件大小 2)设置chunksize参数 3)仅加载必要列 4)使用合适的dtype减少内存占用

## 元数据

- 纠正状态: true
- 纠正措施: 使用chunksize=10000分块读取
- 对话轮次: 15
```

## 标签系统规范

### 标签格式与分类

**动态标签生成规则：**

```
error:<错误类型>          # 根据实际错误动态生成
  示例: error:tool_error, error:reasoning_error, error:workflow_error

success:<成功类型>        # 根据实际成功场景动态生成
  示例: success:user_experience, success:tool_success, success:task_completed

tool:<工具名称>           # 根据使用的工具动态生成
  示例: tool:python_interpreter, tool:web_search, tool:file_read

domain:<应用领域>         # 根据任务领域动态生成
  示例: domain:research, domain:analysis, domain:writing, domain:coding

stage:<任务阶段>          # 根据任务阶段动态生成
  示例: stage:planning, stage:execution, stage:verification, stage:debugging
```

### 标签生成规则

1. 每个记忆**至少包含**一个类型标签（`error:` 或 `success:`）
2. 根据使用的工具添加 `tool:` 标签
3. 根据任务内容添加 `domain:` 标签
4. 根据当前任务阶段添加 `stage:` 标签

## 关键词提取规范

### 关键词来源

1. **错误消息中的关键术语** - 错误类型、库名、函数名
2. **工具名称** - Python库、API服务、工具名
3. **领域术语** - 科研领域特定词汇
4. **参数和值** - 重要的配置参数
5. **解决方案关键词** - 正确的工具、方法名

### 关键词选择原则

- 选择**具有区分度**的词汇
- 优先选择**名词和动词**
- 包含**工具名**和**错误类型**
- 数量控制在 **3-8个** 关键词
- 使用**精确匹配**形式

## 反思生成模板

### 错误记忆反思

当需要记录错误记忆时，必须按照以下结构进行反思：

#### 分析阶段

1. **发生了什么**：详细描述错误或问题的具体情况
2. **为什么发生**：深入分析根本原因，不要停留在表面
3. **影响范围**：评估错误对当前任务和后续任务的影响

#### 反思阶段

1. **错误类型判断**：
   - 工具使用错误？推理过程错误？工作流程错误？其他？

2. **根本原因**（至少50字）：
   - 为什么会犯这个错误？
   - 当时的假设是什么？这些假设有什么问题？

3. **关键教训**（至少30字）：
   - 这个错误教会了我什么？
   - 今后遇到类似情况应该注意什么？

4. **预防策略**（至少30字）：
   - 如何避免再犯同样的错误？
   - 需要建立什么检查机制？

### 成功记忆反思

当需要记录成功记忆时，必须按照以下结构进行反思：

#### 分析阶段

1. **发生了什么**：详细描述成功的具体情况，特别是用户主动引入的经验
2. **为什么成功**：分析成功的关键因素，包括用户提供的宝贵经验
3. **影响范围**：评估成功对当前任务和后续任务的积极影响

#### 反思阶段

1. **成功类型判断**：
   - 用户主动引入的成功经验？工具使用成功？推理正确？工作流程顺畅？任务完成？

2. **成功因素**（至少50字）：
   - 哪些因素导致了成功？特别强调用户主动引入的经验
   - 当时的决策和方法有什么优势？

3. **最佳实践**（至少50字）：
   - 这个成功案例的最佳实践是什么？
   - 如何将用户提供的经验应用到其他类似场景？

4. **关键经验**（至少30字）：
   - 这个成功经验教会了我什么？特别是用户提供的宝贵经验
   - 今后遇到类似情况应该如何处理？

5. **推广策略**（至少30字）：
   - 如何将此成功经验（包括用户引入的经验）推广到其他任务？
   - 需要建立什么标准化流程？

### 示例

#### 错误记忆示例

**错误场景**：使用pandas读取大文件时内存溢出

**反思生成**：

```
root_cause: 尝试一次性加载超过可用内存的大数据集到内存中。使用pd.read_csv()直接读取100万行×250列的CSV文件，导致内存溢出。

what_went_wrong: 直接使用pd.read_csv('large_data.csv')尝试将整个大文件加载到内存，未考虑文件大小和内存限制。

what_should_happen: 在读取大文件前应先检查文件大小，使用chunksize参数分块读取，或仅加载需要的列，使用dtype优化内存。

lesson_learned: 处理大数据集时必须考虑内存限制，不能一次性加载全部数据。需要使用pandas的chunksize参数或dtype参数进行优化。

prevention_strategy: 建立大文件处理检查机制：1)读取前检查文件大小 2)设置chunksize参数 3)仅加载必要列 4)使用合适的dtype减少内存占用。
```

#### 成功记忆示例

**成功场景**：用户主动引入经验 - 使用pandas分块读取大文件并成功分析

**反思生成**：

```
success_factors: 用户主动引入了分块处理大文件的经验，使用chunksize=10000分块读取大文件，仅加载需要的列，使用合适的dtype减少内存占用，成功完成数据分析。

best_practice: 处理大文件时应：1)先检查文件大小 2)设置合理的chunksize 3)仅加载必要列 4)使用dtype优化 5)在分块中进行处理。这些都是用户提供的宝贵经验。

key_experience: 分块处理是处理大文件的有效方法，既可以避免内存溢出，又可以保持处理效率。用户的经验分享帮助我们快速解决了问题。

promotion_strategy: 建立大文件处理的标准化流程，将用户提供的经验整理成最佳实践文档，在团队中推广分块处理的方法。
```

## 混合召回策略

### 召回触发时机

1. **任务开始前**
   - 检索相似任务的成功经验和失败经验
   - 触发条件：用户发起新任务

2. **工具调用前**
   - 检索该工具的成功经验和失败经验
   - 触发条件：准备使用某个工具

3. **遇到错误时**
   - 基于错误消息检索解决方案
   - 触发条件：工具返回错误

4. **成功完成任务后**
   - 记录成功经验并检索相关成功案例
   - 触发条件：任务成功完成

5. **用户反馈后**
   - 检索相关历史记忆
   - 触发条件：用户给出反馈

### 召回方法

**并行执行以下召回：**

1. **标签匹配**（权重25%）
   - 根据tags进行精确或模糊匹配

2. **关键词匹配**（权重20%）
   - 根据keywords进行精确匹配

3. **BM25语义召回**（权重35%）
   - 对context_string和reflection字段进行BM25评分

4. **向量相似度**（权重20%）
   - 对embedding_vector进行余弦相似度计算

### 融合排序

使用 **RRF (Reciprocal Rank Fusion)** 算法进行加权融合：

```
score(doc) = Σ (weight_i / (rank_i(doc) + k)) * weight_factor
```

其中 k=60，weight_factor 根据召回方法调整。

### 召回结果处理

1. 筛选相似度阈值 > 0.5 的记忆
2. 按相关度排序返回 Top-K
3. 如果没有匹配记忆，返回空列表

## 存储结构

```
research-agent-memory/
├── memory_store/
│   ├── memories/                # 记忆文件存储目录
│   │   ├── 2026/                # 按年份组织
│   │   │   ├── 03/              # 按月组织
│   │   │   │   ├── 2026-03-09-550e8400.md  # 记忆文件
│   │   │   │   └── ...
│   └── index/
│       ├── bm25_index.pkl       # BM25索引
│       ├── tag_index.json       # 标签倒排索引
│       └── vector_index.faiss   # 向量索引
├── scripts/
│   ├── __init__.py
│   ├── memory_system.py         # 核心记忆系统
│   ├── embedding.py             # 向量化模块
│   ├── recall.py                # 召回引擎
│   └── cli.py                   # 命令行接口
├── SKILL.md
└── README.md
```

## 使用方式

### 记录记忆

使用 `cli.py record` 命令记录新的记忆：

```bash
python scripts/cli.py record \
    --type <记忆类型> \
    --tags "<标签列表>" \
    --keywords "<关键词列表>" \
    --context "<上下文描述>" \
    --reflection-file <反思文件路径> \
    --snapshot-file <快照文件路径>
```

**参数说明：**
- `--type` (必需): 记忆类型，如 `tool_error`, `success`, `reasoning_error` 等
- `--tags`: 逗号分隔的标签列表，如 `"error:tool_error,tool:python_interpreter,domain:data_processing"`
- `--keywords`: 逗号分隔的关键词列表，如 `"pandas,memory_error,read_csv"`
- `--context`: 上下文描述字符串
- `--reflection-file`: 反思内容JSON文件路径
- `--snapshot-file`: 错误/成功快照JSON文件路径
- `--storage`: (可选) 存储目录路径，默认为 `./memory_store`

**示例：**
```bash
python scripts/cli.py record \
    --type tool_error \
    --tags "error:tool_error,tool:python_interpreter,domain:data_processing" \
    --keywords "pandas,memory_error,read_csv,chunksize" \
    --context "任务：分析100万条科研数据，使用pandas进行数据清洗" \
    --reflection-file ./reflection.json
```

### 召回记忆

使用 `cli.py recall` 命令召回相关记忆：

```bash
python scripts/cli.py recall \
    --query "<查询字符串>" \
    --tags "<标签过滤>" \
    --keywords "<关键词过滤>" \
    --top-k <返回数量> \
    --threshold <相似度阈值>
```

**参数说明：**
- `--query` (必需): 查询字符串，用于混合检索
- `--tags`: 逗号分隔的标签过滤条件，如 `"tool:python_interpreter,domain:data_processing"`
- `--keywords`: 逗号分隔的关键词过滤条件
- `--top-k`: 返回的记忆数量，默认为 5
- `--threshold`: 相似度阈值，默认为 0.3
- `--storage`: (可选) 存储目录路径，默认为 `./memory_store`

**示例：**
```bash
python scripts/cli.py recall \
    --query "pandas读取大文件内存溢出" \
    --tags "tool:python_interpreter" \
    --top-k 3
```

### 上下文增强

使用 `cli.py augment` 命令增强提示词：

```bash
python scripts/cli.py augment \
    --task "<任务描述>" \
    --prompt-file <提示词文件路径> \
    --output <输出文件路径> \
    --top-k <记忆数量> \
    --threshold <相似度阈值>
```

**参数说明：**
- `--task` (必需): 任务描述
- `--prompt-file` (必需): 当前提示词文件路径
- `--output`: (可选) 输出文件路径，不指定则输出到控制台
- `--top-k`: 引用的记忆数量，默认为 3
- `--threshold`: 相似度阈值，默认为 0.5
- `--storage`: (可选) 存储目录路径，默认为 `./memory_store`

**示例：**
```bash
python scripts/cli.py augment \
    --task "分析科研数据集" \
    --prompt-file ./current_prompt.txt \
    --output ./augmented_prompt.txt
```

### 查看统计信息

使用 `cli.py stats` 命令查看记忆系统统计：

```bash
python scripts/cli.py stats [--storage <存储路径>]
```

### 列出记忆

使用 `cli.py list` 命令列出所有记忆：

```bash
python scripts/cli.py list \
    --limit <数量> \
    --offset <偏移量> \
    [--storage <存储路径>]
```

**参数说明：**
- `--limit`: 列出的记忆数量，默认为 100
- `--offset`: 偏移量，默认为 0

### Python API

```python
from scripts.memory_system import ResearchAgentMemory

# 初始化
memory_system = ResearchAgentMemory("./memory_store")

# 记录错误记忆
memory_id = memory_system.record({
    "type": "tool_error",
    "tags": [
        "error:tool_error",
        "tool:python_interpreter",
        "domain:data_processing",
        "stage:execution"
    ],
    "keywords": [
        "pandas",
        "read_csv",
        "memory_error",
        "chunksize"
    ],
    "context_string": "任务：分析100万条科研数据...",
    "error_snapshot": {...},
    "reflection": {
        "root_cause": "...",
        "what_went_wrong": "...",
        "what_should_happen": "...",
        "lesson_learned": "...",
        "prevention_strategy": "..."
    },
    "metadata": {
        "success_after_correction": True,
        "correction_applied": "使用chunksize=10000分块读取",
        "conversation_turn": 15
    }
})

# 动态召回
related_memories = memory_system.recall(
    query="分析科研数据集并进行可视化",
    tags=["domain:data_processing", "stage:planning"],
    top_k=3
)

# 上下文增强
augmented_prompt = memory_system.augment_context(
    task_description="分析科研数据集",
    current_prompt="请分析以下数据..."
)
```

## 注意事项

1. **反思质量**：反思内容必须详细、具体，避免空泛的总结
2. **标签准确性**：确保标签准确反映记忆内容，便于后续召回
3. **关键词选择**：选择具有区分度的关键词，避免过于宽泛
4. **及时记录**：错误发生后尽快记录，确保上下文完整
5. **持续优化**：定期回顾记忆，分析错误模式，改进预防策略
6. **隐私保护**：如涉及敏感信息，进行适当脱敏处理
