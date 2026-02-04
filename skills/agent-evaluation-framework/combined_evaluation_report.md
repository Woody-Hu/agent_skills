# 综合评估报告

## sales_recommendation_evaluator

### 评估结果

#### 方案对比

| 方案 | 模型调用次数 | 总执行时间(秒) | 平均执行时间(秒) |
|------|--------------|----------------|------------------|
| 直接Tool | 5 | 4.84 | 0.97 |
| MCP | 5 | 4.02 | 0.80 |
| Skill | 5 | 5.31 | 1.06 |

### 详细信息

```json
{
  "direct_tool": {
    "model_calls": 5,
    "total_time": 4.843306572769741,
    "average_time": 0.9686613145539482
  },
  "mcp": {
    "model_calls": 5,
    "total_time": 4.0194849993128745,
    "average_time": 0.8038969998625749
  },
  "skill": {
    "model_calls": 5,
    "total_time": 5.309253547352224,
    "average_time": 1.0618507094704448
  }
}
```

## weather_evaluator

### 评估结果

#### 方案对比

| 方案 | 模型调用次数 | 总执行时间(秒) | 平均执行时间(秒) |
|------|--------------|----------------|------------------|
| 直接Tool | 5 | 3.33 | 0.67 |
| MCP | 5 | 2.88 | 0.58 |
| Skill | 5 | 3.92 | 0.78 |

### 详细信息

```json
{
  "direct_tool": {
    "model_calls": 5,
    "total_time": 3.3303446294086667,
    "average_time": 0.6660689258817334
  },
  "mcp": {
    "model_calls": 5,
    "total_time": 2.882872501072499,
    "average_time": 0.5765745002144997
  },
  "skill": {
    "model_calls": 5,
    "total_time": 3.9189968981634298,
    "average_time": 0.783799379632686
  }
}
```

