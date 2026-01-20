---
name: mermaidjs-v11
description: Create diagrams and visualizations using Mermaid.js v11 syntax. Use when generating flowcharts, sequence diagrams, class diagrams, state diagrams, ER diagrams, Gantt charts, user journeys, timelines, architecture diagrams, or any of 24+ diagram types. Supports JavaScript API integration, CLI rendering to SVG/PNG/PDF, theming, configuration, and accessibility features. Essential for documentation, technical diagrams, project planning, system architecture, and visual communication.
---

# Mermaid.js v11

## Overview

Create text-based diagrams using Mermaid.js v11 declarative syntax. Convert code to SVG/PNG/PDF via CLI or render in browsers/markdown files.

## Quick Start

**Basic Diagram Structure:**
```
{diagram-type}
  {diagram-content}
```

**Common Diagram Types:**
- `flowchart` - Process flows, decision trees
- `sequenceDiagram` - Actor interactions, API flows
- `classDiagram` - OOP structures, data models
- `stateDiagram` - State machines, workflows
- `erDiagram` - Database relationships
- `gantt` - Project timelines
- `journey` - User experience flows

See `references/diagram-types.md` for all 24+ types with syntax.

## Creating Diagrams

**Inline Markdown Code Blocks:**
````markdown
```mermaid
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action]
    B -->|No| D[End]
```
````

**Configuration via Frontmatter:**
````markdown
```mermaid
---
theme: dark
---
flowchart LR
    A --> B
```
````

**Comments:** Use `%% ` prefix for single-line comments.

## CLI Usage

Convert `.mmd` files to images:
```bash
# Installation
npm install -g @mermaid-js/mermaid-cli

# Basic conversion
mmdc -i diagram.mmd -o diagram.svg

# With theme and background
mmdc -i input.mmd -o output.png -t dark -b transparent

# Custom styling
mmdc -i diagram.mmd --cssFile style.css -o output.svg
```

See `references/cli-usage.md` for Docker, batch processing, and advanced workflows.

## JavaScript Integration

**HTML Embedding:**
```html
<pre class="mermaid">
  flowchart TD
    A[Client] --> B[Server]
</pre>
<script src="https://cdn.jsdelivr.net/npm/mermaid@latest/dist/mermaid.min.js"></script>
<script>mermaid.initialize({ startOnLoad: true });</script>
```

See `references/integration.md` for Node.js API and advanced integration patterns.

## Configuration & Theming

**Common Options:**
- `theme`: "default", "dark", "forest", "neutral", "base"
- `look`: "classic", "handDrawn"
- `fontFamily`: Custom font specification
- `securityLevel`: "strict", "loose", "antiscript"

See `references/configuration.md` for complete config options, theming, and customization.

## 垂直模块架构图

创建模块垂直分布、模块内元素水平分布且无连接线的架构图，使用 `block-beta` 图表类型：

**基本语法：**
````markdown
```mermaid
block-beta
  columns 3  // 模块内元素数量
  
  subgraph "前端层"
    WebApp[Web应用] API[API网关] CDN[CDN]
  end
  
  subgraph "业务层"
    ServiceA[服务A] ServiceB[服务B] ServiceC[服务C]
  end
  
  subgraph "数据层"
    DB[数据库] Cache[缓存] Storage[存储]
  end
```
````

**带样式的示例：**
````markdown
```mermaid
block-beta
  columns 3
  classDef moduleStyle fill:#f9f,stroke:#333,stroke-width:2px
  classDef elementStyle fill:#bbf,stroke:#f66,stroke-width:1px,rx:5px
  
  subgraph "前端层":::moduleStyle
    WebApp[Web应用]:::elementStyle API[API网关]:::elementStyle CDN[CDN]:::elementStyle
  end
  
  subgraph "业务层":::moduleStyle
    ServiceA[服务A]:::elementStyle ServiceB[服务B]:::elementStyle ServiceC[服务C]:::elementStyle
  end
  
  subgraph "数据层":::moduleStyle
    DB[数据库]:::elementStyle Cache[缓存]:::elementStyle Storage[存储]:::elementStyle
  end
```
````

## Practical Patterns

Load `references/examples.md` for:
- 垂直模块架构图
- Architecture diagrams
- API documentation flows
- Database schemas
- Project timelines
- State machines
- User journey maps

## Resources

- `references/diagram-types.md` - Syntax for all 24+ diagram types
- `references/configuration.md` - Config, theming, accessibility
- `references/cli-usage.md` - CLI commands and workflows
- `references/integration.md` - JavaScript API and embedding
- `references/examples.md` - Practical patterns and use cases