---
name: research-agent-memory
description: "Research agent memory system. Records errors, reflections, and experiences, supports dynamic hybrid recall. Invoke when agent makes mistakes, receives user feedback, or needs to recall past experiences."
---

# Research Agent Memory System

This skill provides error memory recording and dynamic recall capabilities for research agents, helping agents learn from mistakes and continuously improve.

## Trigger Conditions

**Must-trigger scenarios:**

1. **User explicitly requests recording** - User mentions "remember this", "this is wrong", "keep this in mind", "record this" and similar phrases
2. **Tool usage error** - Tool returns error, parameter error, tool unavailable, etc.
3. **Reasoning error** - Wrong thinking, logical error, wrong assumption, inappropriate method selection
4. **Workflow error** - Incorrect execution order, missing steps, task understanding deviation
5. **User feedback** - User points out problems, corrects errors, provides feedback
6. **Task failure** - Task cannot be completed, timeout, results not as expected
7. **Successful execution** - User-initiated success experiences, successful tool calls, correct reasoning, smooth workflow, task completion
8. **Need to recall historical experience** - Before starting a new task, when encountering difficulties, when user asks related questions

## Memory Data Structure

### Markdown Memory File Format

Each memory is stored as a separate Markdown file with filename format: `{timestamp}-{memory_id}.md`

```markdown
---
memory_id: "uuid"
timestamp: "ISO8601 timestamp"
type: "memory type"
tags: ["tag1", "tag2"]
keywords: ["keyword1", "keyword2"]
version: "1.0"
---

# Memory Record

## Context

[Complete context description]

## Snapshot

### Error Information (Error Memory)
- Error Type: [Error Type]
- Error Message: [Error Message]
- Tool Calls: [Tool Call Records]
- Reasoning Chain: [Reasoning Chain]

### Success Information (Success Memory)
- Success Type: [Success Type]
- Result: [Success Result]
- Tool Calls: [Tool Call Records]
- Reasoning Chain: [Reasoning Chain]

## Reflection

### Error Reflection
- Root Cause: [Root Cause Analysis]
- Error Description: [Error Description]
- Correct Approach: [Correct Approach]
- Key Lesson: [Key Lesson]
- Prevention Strategy: [Prevention Strategy]

### Success Reflection
- Success Factors: [Success Factors]
- Best Practice: [Best Practice]
- Key Experience: [Key Experience]
- Promotion Strategy: [Promotion Strategy]

## Metadata

- Correction Status: [Whether Corrected]
- Correction Applied: [Applied Correction Measures]
- Conversation Turn: [Conversation Turn]
```

### Example Memory File

```markdown
---
memory_id: "550e8400-e29b-41d4-a716-446655440000"
timestamp: "2026-03-09T10:00:00Z"
type: "tool_error"
tags: ["error:tool_error", "tool:python_interpreter", "domain:data_processing"]
keywords: ["pandas", "memory_error", "read_csv", "chunksize"]
version: "1.0"
---

# Memory Record

## Context

Task: Analyze 1 million research data records, using pandas for data cleaning. Current step: Read CSV file and convert to DataFrame.

## Snapshot

### Error Information
- Error Type: MemoryError
- Error Message: Unable to allocate 2.5 GiB for an array with shape (1000000, 250)
- Tool Calls: pd.read_csv('large_data.csv')
- Reasoning Chain: Need to read CSV file → Use pandas → Read all data directly

## Reflection

### Error Reflection
- Root Cause: Attempted to load a large dataset exceeding available memory into memory at once
- Error Description: Directly used pd.read_csv('large_data.csv') to load the entire large file into memory without considering file size and memory limitations
- Correct Approach: Before reading large files, check file size, use chunksize parameter for chunked reading, or only load needed columns, use dtype to optimize memory
- Key Lesson: When processing large datasets, memory limitations must be considered; cannot load all data at once
- Prevention Strategy: Establish large file processing check mechanism: 1) Check file size before reading 2) Set chunksize parameter 3) Only load necessary columns 4) Use appropriate dtype to reduce memory usage

## Metadata

- Correction Status: true
- Correction Applied: Use chunksize=10000 for chunked reading
- Conversation Turn: 15
```

## Tag System Specification

### Tag Format and Classification

**Dynamic tag generation rules:**

```
error:<error type>          # Generated dynamically based on actual error
  Examples: error:tool_error, error:reasoning_error, error:workflow_error

success:<success type>        # Generated dynamically based on actual success scenario
  Examples: success:user_experience, success:tool_success, success:task_completed

tool:<tool name>           # Generated dynamically based on used tool
  Examples: tool:python_interpreter, tool:web_search, tool:file_read

domain:<application domain>         # Generated dynamically based on task domain
  Examples: domain:research, domain:analysis, domain:writing, domain:coding

stage:<task stage>          # Generated dynamically based on task stage
  Examples: stage:planning, stage:execution, stage:verification, stage:debugging
```

### Tag Generation Rules

1. Each memory **must contain** at least one type tag (`error:` or `success:`)
2. Add `tool:` tag based on the used tool
3. Add `domain:` tag based on task content
4. Add `stage:` tag based on current task stage

## Keyword Extraction Specification

### Keyword Sources

1. **Key terms from error messages** - Error types, library names, function names
2. **Tool names** - Python libraries, API services, tool names
3. **Domain terms** - Research domain-specific vocabulary
4. **Parameters and values** - Important configuration parameters
5. **Solution keywords** - Correct tools, method names

### Keyword Selection Principles

- Choose **discriminative** vocabulary
- Prioritize **nouns and verbs**
- Include **tool names** and **error types**
- Control number to **3-8 keywords**
- Use **exact match** form

## Reflection Generation Template

### Error Memory Reflection

When recording error memories, reflection must follow this structure:

#### Analysis Phase

1. **What happened**: Detailed description of the specific error or problem
2. **Why it happened**: In-depth analysis of root causes, not just surface-level
3. **Impact scope**: Assess the impact of the error on current and subsequent tasks

#### Reflection Phase

1. **Error type judgment**:
   - Tool usage error? Reasoning process error? Workflow error? Other?

2. **Root cause** (at least 50 characters):
   - Why did this error occur?
   - What were the assumptions at the time? What was wrong with these assumptions?

3. **Key lesson** (at least 30 characters):
   - What did this error teach me?
   - What should I pay attention to in similar situations in the future?

4. **Prevention strategy** (at least 30 characters):
   - How to avoid making the same mistake again?
   - What checking mechanisms need to be established?

### Success Memory Reflection

When recording success memories, reflection must follow this structure:

#### Analysis Phase

1. **What happened**: Detailed description of the specific success, especially user-initiated experiences
2. **Why it succeeded**: Analysis of key success factors, including valuable user-provided experiences
3. **Impact scope**: Assess the positive impact of success on current and subsequent tasks

#### Reflection Phase

1. **Success type judgment**:
   - User-initiated success experience? Successful tool usage? Correct reasoning? Smooth workflow? Task completion?

2. **Success factors** (at least 50 characters):
   - What factors led to success? Especially emphasize user-initiated experiences
   - What were the advantages of the decisions and methods at that time?

3. **Best practice** (at least 50 characters):
   - What are the best practices from this success case?
   - How to apply user-provided experiences to other similar scenarios?

4. **Key experience** (at least 30 characters):
   - What did this success experience teach me? Especially valuable user-provided experiences
   - How to handle similar situations in the future?

5. **Promotion strategy** (at least 30 characters):
   - How to promote this success experience (including user-initiated experiences) to other tasks?
   - What standardized processes need to be established?

### Examples

#### Error Memory Example

**Error scenario**: Memory overflow when reading large files with pandas

**Reflection generation**:

```
root_cause: Attempted to load a large dataset exceeding available memory into memory at once. Used pd.read_csv() to directly read a CSV file with 1 million rows × 250 columns, causing memory overflow.

what_went_wrong: Directly used pd.read_csv('large_data.csv') to load the entire large file into memory without considering file size and memory limitations.

what_should_happen: Before reading large files, check file size, use chunksize parameter for chunked reading, or only load needed columns, use dtype to optimize memory.

lesson_learned: When processing large datasets, memory limitations must be considered; cannot load all data at once. Need to use pandas' chunksize parameter or dtype parameter for optimization.

prevention_strategy: Establish large file processing check mechanism: 1) Check file size before reading 2) Set chunksize parameter 3) Only load necessary columns 4) Use appropriate dtype to reduce memory usage.
```

#### Success Memory Example

**Success scenario**: User-initiated experience - Using pandas chunked reading to successfully analyze large files

**Reflection generation**:

```
success_factors: User actively introduced chunked processing experience for large files, using chunksize=10000 to read large files in chunks, only loading necessary columns, using appropriate dtype to reduce memory usage, successfully completing data analysis.

best_practice: When processing large files: 1) Check file size first 2) Set reasonable chunksize 3) Only load necessary columns 4) Use dtype optimization 5) Process in chunks. These are all valuable experiences provided by the user.

key_experience: Chunked processing is an effective method for handling large files, which can avoid memory overflow while maintaining processing efficiency. User's experience sharing helped us quickly solve the problem.

promotion_strategy: Establish standardized processes for large file processing, organize user-provided experiences into best practice documents, and promote chunked processing methods within the team.
```

## Hybrid Recall Strategy

### Recall Trigger Timing

1. **Before task start**
   - Retrieve successful and failed experiences of similar tasks
   - Trigger condition: User initiates a new task

2. **Before tool call**
   - Retrieve successful and failed experiences of the tool
   - Trigger condition: Preparing to use a tool

3. **When encountering errors**
   - Retrieve solutions based on error messages
   - Trigger condition: Tool returns error

4. **After successful task completion**
   - Record success experience and retrieve related success cases
   - Trigger condition: Task successfully completed

5. **After user feedback**
   - Retrieve related historical memories
   - Trigger condition: User provides feedback

### Recall Methods

**Execute the following recalls in parallel:**

1. **Tag matching** (weight 25%)
   - Exact or fuzzy matching based on tags

2. **Keyword matching** (weight 20%)
   - Exact matching based on keywords

3. **BM25 semantic recall** (weight 35%)
   - BM25 scoring on context_string and reflection fields

4. **Vector similarity** (weight 20%)
   - Cosine similarity calculation on embedding_vector

### Fusion Ranking

Use **RRF (Reciprocal Rank Fusion)** algorithm for weighted fusion:

```
score(doc) = Σ (weight_i / (rank_i(doc) + k)) * weight_factor
```

Where k=60, weight_factor is adjusted based on recall method.

### Recall Result Processing

1. Filter memories with similarity threshold > 0.5
2. Return Top-K sorted by relevance
3. Return empty list if no matching memories

## Storage Structure

```
research-agent-memory/
├── memory_store/
│   ├── memories/                # Memory file storage directory
│   │   ├── 2026/                # Organized by year
│   │   │   ├── 03/              # Organized by month
│   │   │   │   ├── 2026-03-09-550e8400.md  # Memory file
│   │   │   │   └── ...
│   └── index/
│       ├── bm25_index.pkl       # BM25 index
│       ├── tag_index.json       # Tag inverted index
│       └── vector_index.faiss   # Vector index
├── scripts/
│   ├── __init__.py
│   ├── memory_system.py         # Core memory system
│   ├── embedding.py             # Embedding module
│   ├── recall.py                # Recall engine
│   └── cli.py                   # Command line interface
├── SKILL.md
└── README.md
```

## Usage

### Record Memory

Use `cli.py record` command to record new memories:

```bash
python scripts/cli.py record \
    --type <memory type> \
    --tags "<tag list>" \
    --keywords "<keyword list>" \
    --context "<context description>" \
    --reflection-file <reflection file path> \
    --snapshot-file <snapshot file path>
```

**Parameter description:**
- `--type` (required): Memory type, such as `tool_error`, `success`, `reasoning_error`, etc.
- `--tags`: Comma-separated tag list, e.g., `"error:tool_error,tool:python_interpreter,domain:data_processing"`
- `--keywords`: Comma-separated keyword list, e.g., `"pandas,memory_error,read_csv"`
- `--context`: Context description string
- `--reflection-file`: Path to reflection JSON file
- `--snapshot-file`: Path to error/success snapshot JSON file
- `--storage`: (optional) Storage directory path, default is `./memory_store`

**Example:**
```bash
python scripts/cli.py record \
    --type tool_error \
    --tags "error:tool_error,tool:python_interpreter,domain:data_processing" \
    --keywords "pandas,memory_error,read_csv,chunksize" \
    --context "Task: Analyze 1 million research data records, using pandas for data cleaning" \
    --reflection-file ./reflection.json
```

### Recall Memory

Use `cli.py recall` command to recall related memories:

```bash
python scripts/cli.py recall \
    --query "<query string>" \
    --tags "<tag filter>" \
    --keywords "<keyword filter>" \
    --top-k <return count> \
    --threshold <similarity threshold>
```

**Parameter description:**
- `--query` (required): Query string for hybrid search
- `--tags`: Comma-separated tag filter conditions, e.g., `"tool:python_interpreter,domain:data_processing"`
- `--keywords`: Comma-separated keyword filter conditions
- `--top-k`: Number of memories to return, default is 5
- `--threshold`: Similarity threshold, default is 0.3
- `--storage`: (optional) Storage directory path, default is `./memory_store`

**Example:**
```bash
python scripts/cli.py recall \
    --query "pandas memory overflow when reading large files" \
    --tags "tool:python_interpreter" \
    --top-k 3
```

### Context Augmentation

Use `cli.py augment` command to augment prompts:

```bash
python scripts/cli.py augment \
    --task "<task description>" \
    --prompt-file <prompt file path> \
    --output <output file path> \
    --top-k <memory count> \
    --threshold <similarity threshold>
```

**Parameter description:**
- `--task` (required): Task description
- `--prompt-file` (required): Current prompt file path
- `--output`: (optional) Output file path, if not specified, output to console
- `--top-k`: Number of memories to reference, default is 3
- `--threshold`: Similarity threshold, default is 0.5
- `--storage`: (optional) Storage directory path, default is `./memory_store`

**Example:**
```bash
python scripts/cli.py augment \
    --task "Analyze research dataset" \
    --prompt-file ./current_prompt.txt \
    --output ./augmented_prompt.txt
```

### View Statistics

Use `cli.py stats` command to view memory system statistics:

```bash
python scripts/cli.py stats [--storage <storage path>]
```

### List Memories

Use `cli.py list` command to list all memories:

```bash
python scripts/cli.py list \
    --limit <count> \
    --offset <offset> \
    [--storage <storage path>]
```

**Parameter description:**
- `--limit`: Number of memories to list, default is 100
- `--offset`: Offset, default is 0

### Python API

```python
from scripts.memory_system import ResearchAgentMemory

# Initialize
memory_system = ResearchAgentMemory("./memory_store")

# Record error memory
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
    "context_string": "Task: Analyze 1 million research data records...",
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
        "correction_applied": "Use chunksize=10000 for chunked reading",
        "conversation_turn": 15
    }
})

# Dynamic recall
related_memories = memory_system.recall(
    query="Analyze research dataset and visualize",
    tags=["domain:data_processing", "stage:planning"],
    top_k=3
)

# Context augmentation
augmented_prompt = memory_system.augment_context(
    task_description="Analyze research dataset",
    current_prompt="Please analyze the following data..."
)
```

## Notes

1. **Reflection quality**: Reflection content must be detailed and specific, avoiding vague summaries
2. **Tag accuracy**: Ensure tags accurately reflect memory content for easier subsequent recall
3. **Keyword selection**: Choose discriminative keywords, avoiding overly broad terms
4. **Timely recording**: Record errors as soon as they occur to ensure complete context
5. **Continuous optimization**: Regularly review memories, analyze error patterns, and improve prevention strategies
6. **Privacy protection**: If sensitive information is involved, perform appropriate desensitization