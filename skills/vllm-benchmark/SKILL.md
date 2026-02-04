---
name: "vllm-benchmark"
description: "指导如何使用vLLM进行各种类型的基准测试，包括延迟、吞吐量、多模态处理、服务性能和参数扫描等测试方法。"
---

# vLLM Benchmark 执行指南

## 技能目的

本技能旨在帮助开发者理解和使用vLLM的基准测试功能，包括：
- 执行不同类型的基准测试（延迟、吞吐量、多模态等）
- 配置测试参数以获得准确的性能数据
- 运行参数扫描以找到最佳配置
- 遵循最佳实践确保测试结果的可靠性

## 什么是vLLM Benchmark？

vLLM Benchmark 是 vLLM 提供的一套命令行工具，用于测试和评估模型在不同场景下的性能表现，包括：
- **延迟测试**：测量模型生成响应的速度
- **吞吐量测试**：测量模型在单位时间内处理请求的能力
- **多模态处理器测试**：测试模型处理多模态输入的性能
- **服务性能测试**：模拟真实服务场景下的性能
- **参数扫描**：通过测试不同参数组合找到最佳配置

## 安装和准备

### 安装 vLLM

```bash
pip install vllm
```

### 准备模型

确保你有可用的模型，可以是：
- Hugging Face 模型名称（如 `Qwen/Qwen3-0.6B`）
- 本地模型路径

### 准备数据集

某些测试需要特定的数据集，如：
- `sharegpt`：用于对话模型测试
- `random`：随机生成的输入
- `sonnet`：特定格式的测试数据
- `burstgpt`：模拟突发流量场景

## 1. 延迟测试 (Latency Benchmark)

### 基本用法

```bash
vllm bench latency --model <model_name> [options]
```

### 主要参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `--model` | 模型名称或路径 | `Qwen/Qwen3-0.6B` |
| `--input-len` | 输入长度 | 32 |
| `--output-len` | 输出长度 | 128 |
| `--batch-size` | 批处理大小 | 8 |
| `--n` | 每个提示生成的序列数 | 1 |
| `--use-beam-search` | 是否使用束搜索 | False |
| `--num-iters-warmup` | 预热迭代次数 | 10 |
| `--num-iters` | 测试迭代次数 | 30 |
| `--profile` | 是否分析生成过程 | False |
| `--output-json` | 保存结果的JSON路径 | - |

### 示例

```bash
# 测试基本延迟
vllm bench latency --model meta-llama/Llama-2-7b-hf --input-len 128 --output-len 256 --batch-size 1

# 保存结果到JSON
vllm bench latency --model meta-llama/Llama-2-7b-hf --output-json latency_results.json

# 使用束搜索测试
vllm bench latency --model meta-llama/Llama-2-7b-hf --use-beam-search --n 4
```

## 2. 吞吐量测试 (Throughput Benchmark)

### 基本用法

```bash
vllm bench throughput --model <model_name> [options]
```

### 主要参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `--backend` | 后端类型 (`vllm`, `hf`, `mii`, `vllm-chat`) | `vllm` |
| `--dataset-name` | 数据集名称 | `sharegpt` |
| `--input-len` | 输入长度 | - |
| `--output-len` | 输出长度 | - |
| `--num-prompts` | 处理的提示数量 | 1000 |
| `--async-engine` | 使用异步引擎 | False |
| `--output-json` | 保存结果的JSON路径 | - |

### 示例

```bash
# 基本吞吐量测试
vllm bench throughput --model meta-llama/Llama-2-7b-hf

# 使用随机数据集
vllm bench throughput --model meta-llama/Llama-2-7b-hf --dataset-name random --random-input-len 128 --random-output-len 256

# 测试异步引擎性能
vllm bench throughput --model meta-llama/Llama-2-7b-hf --async-engine
```

## 3. 多模态处理器测试 (MM Processor Benchmark)

### 基本用法

```bash
vllm bench mm-processor --model <model_name> [options]
```

### 主要参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `--dataset-name` | 数据集名称 | `random-mm` |
| `--random-mm-base-items-per-request` | 每个请求的基础多模态项目数 | 1 |
| `--random-mm-limit-mm-per-prompt` | 每个提示的多模态项目限制 | `{"image": 255, "video": 1}` |
| `--random-mm-bucket-config` | 多模态项目采样配置 | 见下文 |

### 示例

```bash
# 基本多模态测试
vllm bench mm-processor --model llava-hf/llava-1.5-7b-hf

# 配置图像采样
vllm bench mm-processor --model llava-hf/llava-1.5-7b-hf --random-mm-bucket-config '{"(256, 256, 1)": 0.5, "(720, 1280, 1)": 0.5}'
```

## 4. 服务性能测试 (Serve Benchmark)

### 基本用法

```bash
vllm bench serve --model <model_name> [options]
```

### 主要参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `--dataset-name` | 数据集名称 | `sharegpt` |
| `--arrival-rate` | 请求到达速率（每秒请求数） | 1.0 |
| `--duration` | 测试持续时间（秒） | 60 |
| `--timeout` | 请求超时时间（秒） | 300 |
| `--output-json` | 保存结果的JSON路径 | - |

### 示例

```bash
# 基本服务测试
vllm bench serve --model meta-llama/Llama-2-7b-hf

# 测试高流量场景
vllm bench serve --model meta-llama/Llama-2-7b-hf --arrival-rate 10.0 --duration 120
```

## 5. 参数扫描 (Sweep)

### 5.1 基本扫描

```bash
vllm bench sweep serve --model <model_name> --parameters <parameter_config> [options]
```

### 5.2 SLA 扫描

```bash
vllm bench sweep serve_sla --model <model_name> --sla <sla_config> [options]
```

### 主要参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `--parameters` | 要扫描的参数配置 | - |
| `--sla` | SLA 要求配置 | - |
| `--output-dir` | 结果输出目录 | - |
| `--num-runs` | 每个参数组合的运行次数 | 1 |

### 示例

```bash
# 扫描不同批处理大小
vllm bench sweep serve --model meta-llama/Llama-2-7b-hf --parameters '{"max_num_seqs": [16, 32, 64]}'

# 扫描满足SLA要求的配置
vllm bench sweep serve_sla --model meta-llama/Llama-2-7b-hf --sla '{"p99_latency": 10.0}' --parameters '{"max_num_seqs": [16, 32, 64]}'
```

## 6. 结果可视化

### 6.1 绘制扫描结果

```bash
vllm bench sweep plot --input-dir <sweep_output_dir> --output <plot_file>
```

### 6.2 绘制帕累托前沿

```bash
vllm bench sweep plot_pareto --input-dir <sweep_output_dir> --output <plot_file>
```

### 示例

```bash
# 绘制扫描结果
vllm bench sweep plot --input-dir sweep_results --output throughput_vs_latency.png

# 绘制帕累托前沿
vllm bench sweep plot_pareto --input-dir sweep_results --output pareto_frontier.png
```

## 高级配置

### JSON 命令行参数

vLLM 支持使用 JSON 格式传递复杂参数：

```bash
# 两种等效的方式
vllm bench latency --json-arg '{"model": "Qwen/Qwen3-0.6B", "input_len": 128}'
vllm bench latency --json-arg.model "Qwen/Qwen3-0.6B" --json-arg.input_len 128
```

### 列表参数

对于列表类型的参数，可以使用 `+` 语法：

```bash
vllm bench sweep serve --parameters '{"max_num_seqs": [16, 32]}'
vllm bench sweep serve --parameters.max_num_seqs+ 16 --parameters.max_num_seqs+ 32
```

## 最佳实践

### 1. 测试设计

- **合理的预热**：使用足够的预热迭代次数，确保模型和系统达到稳定状态
- **足够的测试时间**：对于吞吐量测试，确保测试持续足够长的时间以获得代表性结果
- **控制变量**：一次只改变一个参数，以便准确评估其影响
- **多次运行**：对每个配置运行多次测试，取平均值以减少随机性

### 2. 参数选择

- **输入长度**：选择与实际使用场景相匹配的输入长度
- **输出长度**：选择合理的输出长度，过长会导致测试时间过长
- **批处理大小**：根据硬件内存和预期负载选择合适的批处理大小
- **并发度**：对于服务测试，选择与预期真实场景相匹配的并发度

### 3. 硬件考虑

- **GPU 内存**：确保有足够的 GPU 内存加载模型
- **CPU 和内存**：确保 CPU 和系统内存不会成为瓶颈
- **网络**：对于分布式测试，确保网络连接稳定
- **温度**：长时间测试可能导致 GPU 温度升高，影响性能

### 4. 常见问题

- **内存不足**：减小批处理大小或使用更小的模型
- **测试时间过长**：减少测试迭代次数或使用更小的数据集
- **结果不稳定**：增加测试次数或检查系统负载
- **GPU 利用率低**：调整批处理大小或并发度

## 示例工作流程

### 完整性能评估流程

1. **延迟测试**：
   ```bash
   vllm bench latency --model meta-llama/Llama-2-7b-hf --input-len 128 --output-len 256 --batch-size 1 --num-iters 50
   ```

2. **吞吐量测试**：
   ```bash
   vllm bench throughput --model meta-llama/Llama-2-7b-hf --dataset-name random --random-input-len 128 --random-output-len 256 --num-prompts 2000
   ```

3. **服务性能测试**：
   ```bash
   vllm bench serve --model meta-llama/Llama-2-7b-hf --arrival-rate 5.0 --duration 120
   ```

4. **参数扫描**：
   ```bash
   vllm bench sweep serve --model meta-llama/Llama-2-7b-hf --parameters '{"max_num_seqs": [16, 32, 64], "tensor_parallel_size": [1, 2]}' --output-dir sweep_results
   ```

5. **结果可视化**：
   ```bash
   vllm bench sweep plot --input-dir sweep_results --output performance_comparison.png
   vllm bench sweep plot_pareto --input-dir sweep_results --output pareto_frontier.png
   ```

## 总结

vLLM Benchmark 提供了一套强大的工具，用于全面评估模型在不同场景下的性能表现。通过合理使用这些工具，你可以：

1. **了解模型性能**：掌握模型在不同配置下的延迟和吞吐量表现
2. **优化部署配置**：通过参数扫描找到最佳的部署参数组合
3. **预测服务能力**：评估模型在真实服务场景下的表现
4. **比较不同模型**：在相同条件下比较不同模型的性能
5. **识别性能瓶颈**：发现影响性能的关键因素

通过遵循本指南中的最佳实践，你可以获得准确、可靠的性能数据，为模型部署和优化提供有力支持。