---
name: "langchain-middleware"
description: "指导如何创建和使用LangChain Middleware，包括应用场景、内置组件、自定义实现方法和最佳实践。"
---

# LangChain Middleware 创建指南

## 技能目的

本技能旨在帮助开发者理解和使用LangChain Middleware，包括：
- 了解Middleware的应用场景和价值
- 掌握内置Middleware的使用方法
- 学习如何创建自定义Middleware
- 遵循最佳实践设计和实现Middleware

## 什么是Middleware？

Middleware 是 LangChain 中用于更精细控制代理行为的机制，它可以：
- 跟踪代理行为，进行日志记录、分析和调试
- 转换提示词、工具选择和输出格式
- 添加重试、回退和提前终止逻辑
- 应用速率限制、护栏和PII检测

## 应用场景

Middleware 适用于以下场景：

### 1. 监控和调试
- 记录代理执行过程中的详细信息
- 分析模型调用和工具使用情况
- 调试复杂的代理行为

### 2. 性能优化
- 自动总结对话历史，减少令牌使用
- 实现请求缓存，避免重复计算
- 应用速率限制，防止过度使用API

### 3. 可靠性增强
- 添加重试机制，处理临时故障
- 实现模型回退，当主要模型不可用时切换到备用模型
- 添加人类在环（Human-in-the-Loop）审批流程

### 4. 安全和合规
- 检测和处理个人身份信息（PII）
- 应用内容过滤和护栏
- 监控和限制工具使用

### 5. 用户体验优化
- 自定义输出格式和响应风格
- 实现更智能的对话管理
- 添加个性化的交互逻辑

## 内置Middleware

LangChain 提供了多种预构建的 Middleware，适用于常见场景：

| Middleware | 描述 |
|------------|------|
| Summarization | 当接近令牌限制时自动总结对话历史 |
| Human-in-the-loop | 暂停执行以获得人类对工具调用的批准 |
| Model call limit | 限制模型调用次数以防止过高成本 |
| Tool call limit | 通过限制调用次数控制工具执行 |
| Model fallback | 当主模型失败时自动回退到替代模型 |
| PII detection | 检测和处理个人身份信息 |
| To-do list | 为代理配备任务规划和跟踪能力 |
| LLM tool selector | 在调用主模型之前使用LLM选择相关工具 |
| Tool retry | 使用指数退避自动重试失败的工具调用 |
| Model retry | 使用指数退避自动重试失败的模型调用 |
| LLM tool emulator | 使用LLM模拟工具执行以进行测试 |
| Context editing | 通过修剪或清除工具使用来管理对话上下文 |
| Shell tool | 向代理公开持久的shell会话以执行命令 |
| File search | 提供对文件系统文件的Glob和Grep搜索工具 |

### 内置Middleware使用示例

#### Summarization Middleware

```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model="gpt-4.1",
    tools=[your_weather_tool, your_calculator_tool],
    middleware=[
        SummarizationMiddleware(
            model="gpt-4.1-mini",
            trigger=("tokens", 4000),
            keep=("messages", 20),
        ),
    ],
)
```

#### Human-in-the-Loop Middleware

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware

agent = create_agent(
    model="gpt-4.1",
    tools=[your_dangerous_tool],
    middleware=[
        HumanInTheLoopMiddleware(
            approval_prompt="批准以下工具调用: {tool_call}",
            timeout=300,
        ),
    ],
)
```

## 如何创建自定义Middleware

LangChain 提供了两种创建自定义 Middleware 的方法：

### 1. 基于装饰器的Middleware

适合快速创建单个钩子的Middleware，使用装饰器包装单个函数。

#### 可用装饰器

**节点风格钩子：**
- `@before_agent` - 在代理开始前运行（每次调用一次）
- `@before_model` - 在每次模型调用前运行
- `@after_model` - 在每次模型响应后运行
- `@after_agent` - 在代理完成后运行（每次调用一次）

**包装风格钩子：**
- `@wrap_model_call` - 用自定义逻辑包装每个模型调用
- `@wrap_tool_call` - 用自定义逻辑包装每个工具调用

**便利装饰器：**
- `@dynamic_prompt` - 生成动态系统提示

#### 装饰器示例

```python
from langchain.agents.middleware import (
    before_model,
    wrap_model_call,
    AgentState,
    ModelRequest,
    ModelResponse,
)
from langchain.agents import create_agent
from langgraph.runtime import Runtime
from typing import Any, Callable


@before_model
def log_before_model(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    print(f"即将调用模型，当前有 {len(state['messages'])} 条消息")
    return None

@wrap_model_call
def retry_model(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    for attempt in range(3):
        try:
            return handler(request)
        except Exception as e:
            if attempt == 2:
                raise
            print(f"重试 {attempt + 1}/3，错误: {e}")

agent = create_agent(
    model="gpt-4.1",
    middleware=[log_before_model, retry_model],
    tools=[...]
)
```

### 2. 基于类的Middleware

适合创建更复杂的、包含多个钩子的Middleware。

#### 类示例

```python
from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langchain.messages import AIMessage
from langgraph.runtime import Runtime
from typing import Any

class MessageLimitMiddleware(AgentMiddleware):
    def __init__(self, max_messages: int = 50):
        super().__init__()
        self.max_messages = max_messages

    @hook_config(can_jump_to=["end"])
    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        if len(state["messages"]) == self.max_messages:
            return {
                "messages": [AIMessage("对话限制已达到。")],
                "jump_to": "end"
            }
        return None

    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"模型返回了响应，当前消息数: {len(state['messages'])}")
        return None

agent = create_agent(
    model="gpt-4.1",
    middleware=[MessageLimitMiddleware(max_messages=30)],
    tools=[...]
)
```

## Middleware 执行流程

代理执行循环涉及以下步骤：
1. 调用模型
2. 让模型选择要执行的工具
3. 执行工具
4. 重复上述步骤，直到模型不再调用工具

Middleware 在这些步骤的前后暴露钩子：

```
before_agent
  └── 循环开始
      ├── before_model
      │   └── 模型调用
      │       └── after_model
      ├── 工具选择
      ├── 工具执行
      └── 循环继续
  └── 循环结束
after_agent
```

## 最佳实践

### 1. 设计原则

- **单一职责：** 每个Middleware应专注于一个特定功能
- **可配置性：** 提供合理的配置选项，使其适应不同场景
- **错误处理：** 妥善处理异常，避免崩溃整个代理
- **性能考虑：** 避免在Middleware中执行耗时操作
- **可测试性：** 设计易于测试的Middleware

### 2. 实现技巧

- **使用适当的钩子类型：** 对于简单的日志记录使用节点钩子，对于复杂的控制流使用包装钩子
- **合理使用状态：** 仅在必要时修改状态，保持状态变化的可预测性
- **考虑执行顺序：** Middleware的添加顺序会影响执行顺序
- **提供清晰的文档：** 为自定义Middleware添加详细的文档和示例

### 3. 性能优化

- **缓存频繁使用的数据：** 避免重复计算
- **批量处理：** 对于日志等操作，考虑批量处理
- **懒加载：** 仅在需要时初始化资源
- **合理的触发条件：** 为自动总结等功能设置合适的触发阈值

### 4. 可靠性考虑

- **优雅降级：** 当Middleware失败时，应允许代理继续执行
- **重试策略：** 为网络请求等不稳定操作实现合理的重试策略
- **回退机制：** 考虑当主要功能不可用时的回退方案
- **超时处理：** 为可能耗时的操作设置合理的超时

## 示例：创建实用的自定义Middleware

### 1. 重试和回退Middleware

```python
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from typing import Callable

class RobustModelMiddleware(AgentMiddleware):
    def __init__(self, max_retries: int = 3, fallback_model: str = None):
        super().__init__()
        self.max_retries = max_retries
        self.fallback_model = fallback_model

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        # 尝试使用主模型
        for attempt in range(self.max_retries):
            try:
                return handler(request)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    # 最后一次尝试失败，使用回退模型
                    if self.fallback_model:
                        print(f"主模型失败，尝试使用回退模型: {self.fallback_model}")
                        original_model = request.model
                        request.model = self.fallback_model
                        try:
                            return handler(request)
                        finally:
                            request.model = original_model
                    raise
                print(f"重试 {attempt + 1}/{self.max_retries}，错误: {e}")
```

### 2. 令牌使用监控Middleware

```python
from langchain.agents.middleware import before_model, after_model, AgentState
from langgraph.runtime import Runtime
from typing import Any

class TokenMonitorMiddleware:
    def __init__(self):
        self.total_tokens = 0
        self.request_count = 0

    @before_model
    def before_model_call(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        self.request_count += 1
        print(f"开始第 {self.request_count} 次模型调用")
        return None

    @after_model
    def after_model_call(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        # 假设我们可以从响应中获取令牌使用情况
        # 实际实现中需要根据具体模型API进行调整
        if hasattr(state, 'last_response') and hasattr(state.last_response, 'usage'):
            usage = state.last_response.usage
            self.total_tokens += usage.total_tokens
            print(f"模型调用完成，本次使用 {usage.total_tokens} 令牌，累计使用 {self.total_tokens} 令牌")
        return None
```

## 常见问题

### 1. Middleware 不执行

**可能原因：**
- 没有正确添加到代理的 middleware 列表中
- 钩子方法名称不正确
- 装饰器使用错误

**解决方案：**
- 检查 middleware 参数是否正确传递给 create_agent
- 确认钩子方法名称和签名正确
- 验证装饰器使用是否符合文档要求

### 2. Middleware 导致代理崩溃

**可能原因：**
- Middleware 中存在未捕获的异常
- 状态修改导致了不一致的状态
- 无限循环或死锁

**解决方案：**
- 在 Middleware 中添加完整的错误处理
- 谨慎修改状态，确保状态一致性
- 避免在 Middleware 中执行可能导致无限循环的操作

### 3. Middleware 执行顺序问题

**可能原因：**
- Middleware 添加顺序不正确
- 多个 Middleware 修改了相同的状态

**解决方案：**
- 考虑 Middleware 的执行顺序，将依赖的 Middleware 放在前面
- 避免多个 Middleware 修改相同的状态，或确保修改顺序合理

## 总结

LangChain Middleware 是一个强大的机制，可以：

1. **增强代理能力：** 通过添加重试、总结、监控等功能
2. **精细控制行为：** 在代理执行的各个阶段插入自定义逻辑
3. **提高可靠性：** 处理异常情况，提供回退机制
4. **优化性能：** 减少令牌使用，提高执行效率
5. **改善用户体验：** 自定义输出，添加个性化逻辑

通过遵循最佳实践，创建和使用合适的 Middleware，可以显著提升 LangChain 代理的质量和可靠性。