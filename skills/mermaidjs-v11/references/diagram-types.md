# Mermaid.js Diagram Types

Comprehensive syntax reference for all 24+ diagram types in Mermaid.js v11.

## Core Diagrams

### Flowchart
Process flows, decision trees, workflows.

**Syntax:**
```
flowchart {direction}
  {nodeId}[{label}] {arrow} {nodeId}[{label}]
```

**Directions:** TB/TD (top-bottom), BT, LR (left-right), RL
**Shapes:** `()` round, `[]` rect, `{}` diamond, `{{}}` hexagon, `(())` circle
**Arrows:** `-->` solid, `-.->` dotted, `==>` thick
**Subgraphs:** Group related nodes

### Sequence Diagram
Actor interactions, API flows, message sequences.

**Syntax:**
```
sequenceDiagram
  participant A as Actor
  A->>B: Message
  activate B
  B-->>A: Response
  deactivate B
```

**Arrows:** `->` solid, `->>` arrow, `-->` dotted, `-x` cross, `-)` async
**Features:** Loops, alternatives, parallel, optional, critical regions

### Class Diagram
OOP structures, inheritance, relationships.

**Syntax:**
```
classDiagram
  class Animal {
    +String name
    -int age
    +void eat()
  }
  Animal <|-- Dog : inherits
```

**Visibility:** `+` public, `-` private, `#` protected, `~` package
**Relationships:** `<|--` inheritance, `*--` composition, `o--` aggregation, `-->` association

### State Diagram
State machines, transitions, workflows.

**Syntax:**
```
stateDiagram-v2
  [*] --> State1
  State1 --> State2 : transition
  State2 --> [*]
```

**Features:** Composite states, choice points, forks/joins, concurrency

### ER Diagram
Database relationships, schemas.

**Syntax:**
```
erDiagram
  CUSTOMER ||--o{ ORDER : places
  ORDER ||--|{ LINE_ITEM : contains
```

**Cardinality:** `||` one, `|o` zero-one, `}|` one-many, `}o` zero-many

## Planning Diagrams

### Gantt Chart
Project timelines, schedules.

**Syntax:**
```
gantt
  title Project
  dateFormat YYYY-MM-DD
  section Phase1
    Task1 :done, 2024-01-01, 5d
    Task2 :active, after Task1, 3d
```

**Status:** `done`, `active`, `crit`, `milestone`

### User Journey
Experience flows, satisfaction tracking.

**Syntax:**
```
journey
  title User Journey
  section Shopping
    Browse: 5: Customer
    Add to cart: 3: Customer, System
```

**Scores:** 1-5 satisfaction levels

### Kanban
Task boards, workflow stages.

**Syntax:**
```
kanban
  Todo[Task Board]
    task1[Implement API]
    @{ assigned: "Dev1", priority: "High" }
  InProgress[In Progress]
    task2[Fix bug]
```

### Quadrant Chart
Prioritization, trend analysis.

**Syntax:**
```
quadrantChart
  x-axis Low --> High
  y-axis Low --> High
  Item A: [0.3, 0.6]
```

## Architecture Diagrams

### C4 Diagram
System architecture, components.

**Syntax:**
```
C4Context
  Person(user, "User")
  System(app, "Application")
  Rel(user, app, "Uses")
```

### Architecture Diagram
Cloud infrastructure, services.

**Syntax:**
```
architecture-beta
  service api(server)[API]
  service db(database)[Database]
  api:R --> L:db
```

**Icons:** cloud, database, disk, internet, server, or iconify.design icons

### Block Diagram
Module dependencies, networks, vertical module architectures.

**Syntax:**
```
block-beta
  columns 3
  a["Block A"] b["Block B"]
  a --> b
```

**Shapes:** rounded, stadium, cylinder, diamond, trapezoid, hexagon

**垂直模块布局：**
创建模块垂直分布、模块内元素水平分布且无连接线的架构图。

**语法：**
```
block-beta
  columns {num-columns}  // 模块内元素数量
  // 垂直层1
  subgraph "模块名称1"
    元素1[标签1] 元素2[标签2] 元素3[标签3]
  end
  // 垂直层2
  subgraph "模块名称2"
    元素4[标签4] 元素5[标签5]
  end
  // 垂直层3
  subgraph "模块名称3"
    元素6[标签6] 元素7[标签7] 元素8[标签8] 元素9[标签9]
  end
```

**示例：**
```
block-beta
  columns 3
  
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

**带样式的示例：**
```
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

## Data Visualization

### Pie Chart
Proportions, distributions.

**Syntax:**
```
pie showData
  "Category A" : 45.5
  "Category B" : 30.0
```

### XY Chart
Trends, comparisons.

**Syntax:**
```
xychart-beta
  x-axis [jan, feb, mar]
  y-axis "Sales" 0 --> 100
  line [30, 45, 60]
  bar [25, 40, 55]
```

### Sankey
Flow visualization, resource allocation.

**Syntax:**
```
sankey-beta
  Source,Target,Value
  A,B,10
  B,C,5
```

### Radar Chart
Multi-dimensional comparison.

**Syntax:**
```
radar-beta
  axis Skill1, Skill2, Skill3
  curve Team1{3,4,5}
  curve Team2{4,3,4}
```

### Treemap
Hierarchical proportions.

**Syntax:**
```
treemap-beta
  "Root"
    "Category A"
      "Item 1": 100
      "Item 2": 200
```

## Technical Diagrams

### Git Graph
Branching strategies, workflows.

**Syntax:**
```
gitGraph
  commit
  branch develop
  checkout develop
  commit
  checkout main
  merge develop
```

### Timeline
Chronological events, milestones.

**Syntax:**
```
timeline
  2024 : Event A : Event B
  2025 : Event C
```

### Packet Diagram
Network protocols, structures.

**Syntax:**
```
packet-beta
  0-15: "Header"
  16-31: "Data"
```

### ZenUML Sequence
Alternative sequence syntax.

**Syntax:**
```
zenuml
  A.method() {
    B.process()
    return result
  }
```

### Mindmap
Brainstorming, hierarchies.

**Syntax:**
```
mindmap
  root((Central Idea))
    Branch 1
      Sub 1
      Sub 2
    Branch 2
```

### Requirement Diagram
SysML requirements, traceability.

**Syntax:**
```
requirementDiagram
  requirement req1 {
    id: R1
    text: User shall login
    risk: Medium
  }
```

## Quick Reference

| Type | Best For | Complexity |
|------|----------|------------|
| Flowchart | Processes | Low |
| Sequence | Interactions | Medium |
| Class | OOP | High |
| State | Behaviors | Medium |
| ER | Databases | Low |
| Gantt | Timelines | Medium |
| Architecture | Systems | High |
