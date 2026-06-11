# 图表规范（Mermaid）

architect 与 writer 出图统一规范。所有图以 Mermaid 源码存放于 `architecture/diagrams/*.mmd`，可选用 `mmdc` 渲染。

## 一、网络拓扑图（graph TB/LR）

体现安全域、链路、冗余：
```mermaid
graph TB
  Internet((互联网)) --> FW[边界防火墙/IPS]
  FW --> WAF[Web应用防火墙]
  WAF --> LB[负载均衡集群]
  subgraph DMZ[DMZ区]
    LB --> Web1[Web节点1]
    LB --> Web2[Web节点2]
  end
  subgraph Core[核心区]
    Web1 --> App[应用集群]
    Web2 --> App
    App --> DB[(主库)]
    DB -. 实时同步 .-> DBbak[(备库)]
  end
```

## 二、云/部署架构图

体现可用区、高可用、容灾：
```mermaid
graph LR
  subgraph AZ1[可用区A]
    LB1[负载均衡] --> APP1[应用集群]
    APP1 --> CACHE1[Redis]
    APP1 --> DB1[(数据库主)]
  end
  subgraph AZ2[可用区B 容灾]
    LB2[负载均衡] --> APP2[应用集群]
    APP2 --> DB2[(数据库备)]
  end
  DB1 -. 跨AZ同步 .-> DB2
```

## 三、系统功能模块图（graph TD）

模块划分与数据流：
```mermaid
graph TD
  U[用户/终端] --> GW[API网关]
  GW --> M1[用户管理模块]
  GW --> M2[业务处理模块]
  GW --> M3[数据分析模块]
  M1 --> DS[(数据中心)]
  M2 --> DS
  M3 --> DS
  M2 --> MQ[消息队列]
```

## 三·补、软件类总体架构四图（软件开发类必含）

软件开发类技术方案的"系统总体技术架构"必须包含以下四图（缺一视为设计不完整）：

### 1. 逻辑分层图（graph TB）

表现层/应用层/服务层/数据层逻辑分层与各层职责：
```mermaid
graph TB
  subgraph L1[表现层]
    UI[Web/移动端 UI]
  end
  subgraph L2[应用层]
    API[API网关] --> BFF[聚合服务]
  end
  subgraph L3[服务层]
    S1[业务服务A] 
    S2[业务服务B]
  end
  subgraph L4[数据层]
    DB[(数据库)]
    CACHE[(缓存)]
  end
  UI --> API
  BFF --> S1 --> DB
  BFF --> S2 --> CACHE
```

### 2. 数据主流向图（flowchart LR）

核心业务数据 产生→处理→存储→消费 的主流向：
```mermaid
flowchart LR
  SRC[数据产生/采集] --> ETL[校验/处理]
  ETL --> STORE[(主存储)]
  STORE --> ANA[分析/计算]
  ANA --> CONS[消费:报表/接口/前端]
  STORE -. 同步 .-> DW[(数据仓库)]
```

### 3. 组件图（graph LR）

主要组件（服务/模块/中间件）及依赖调用关系：
```mermaid
graph LR
  GW[API网关] --> AUTH[认证组件]
  GW --> ORD[订单组件]
  GW --> USR[用户组件]
  ORD --> MQ[[消息队列]]
  ORD --> ODB[(订单库)]
  USR --> UDB[(用户库)]
  ORD -. 调用 .-> USR
```

### 4. 部署图（graph TB）

物理/云部署拓扑：节点、网络、中间件、数据库部署与高可用：
```mermaid
graph TB
  subgraph Client[客户端]
    B[浏览器/App]
  end
  subgraph DMZ[DMZ]
    LB[负载均衡]
  end
  subgraph AppZone[应用区·双节点]
    N1[应用节点1] 
    N2[应用节点2]
  end
  subgraph DataZone[数据区]
    DBm[(数据库主)] -. 主备 .-> DBs[(数据库备)]
    RDS[(缓存集群)]
  end
  B --> LB --> N1
  LB --> N2
  N1 --> DBm
  N2 --> DBm
  N1 --> RDS
```

> 类图可用 `classDiagram`，用于功能模块的"类与算法设计"；用例可用 `graph`/`flowchart` 表达用例关系或参与者-用例图。

## 四、流程时序图（sequenceDiagram）

关键业务/服务响应流程：
```mermaid
sequenceDiagram
  participant U as 用户
  participant S as 服务台
  participant E as 工程师
  U->>S: 提交故障工单
  S->>E: 15分钟内派单
  E->>U: 现场/远程处理
  E->>S: 2小时内恢复并回单
```

## 五、甘特图（gantt，进度计划）

```mermaid
gantt
  title 项目实施进度计划
  dateFormat YYYY-MM-DD
  section 设计阶段
  需求调研 :a1, 2026-01-01, 10d
  方案设计 :a2, after a1, 15d
  section 实施阶段
  开发/集成 :a3, after a2, 30d
  测试      :a4, after a3, 15d
  section 验收
  试运行   :a5, after a4, 20d
  竣工验收 :a6, after a5, 5d
```

## 六、类图（classDiagram，功能模块"类与算法设计"用）

```mermaid
classDiagram
  class OrderService {
    +createOrder(req) Order
    +cancel(id) bool
    -validate(req) bool
  }
  class Order {
    +id: string
    +status: string
    +items: Item[]
  }
  OrderService --> Order : 创建/管理
```

## 规范要点

1. **语法可解析**：节点/边/方向完整，自检无语法错。
2. **中文标签**：节点名用中文，简洁明确。
3. **图文一致**：图中组件必须在正文有对应说明。
4. **抽象适度**：总体图不超过 ~20 节点，复杂部分拆子图。
5. **渲染降级**：无 mmdc 时保留源码并在正文内嵌 ```mermaid 代码块。
