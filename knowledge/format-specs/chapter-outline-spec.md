# 章纲格式规范

`chapters/ch-{N}-{slug}.md` 是单章撰写指令，由 bid-agent 依据大纲拆出（或作者调整），writer 据此撰写。

## 标准结构

```markdown
---
chapter: 3
slug: tech-architecture
title: 技术方案 - 总体技术架构
status: outline   # outline → draft → reviewed → archived
bid_type: service
---

## 承接评分点
| 评分点 | 分值 | 应答要求 |
|--------|------|---------|
| 3.1 总体架构合理性 | 8 | 提供架构图+论证 |
| 3.2 网络安全设计 | 6 | 安全域+措施 |

## 本章范围
- 写什么：总体技术架构、安全设计、容灾
- 不写什么：详细服务方案（第4章）

## 引用依据
- architecture/overall-design.md、architecture/diagrams/topology.mmd
- 检索素材：retriever 提供（.agent/task/retrieval-result.md）

## 重写记录（评分闭环回填）
- 第N轮失分项与改进建议（由 bid-agent 从 scoring-report 带入 write-order）
```

## status 流转

| status | 含义 |
|--------|------|
| outline | 章纲已拆，待撰写 |
| draft | writer 已产出草稿 |
| reviewed | reviewer 审查通过 / expert 评分达标 |
| archived | updater 已定稿归档 |

## 原则
- 每章承接评分点必须来自 scoring-checklist.md，可追溯
- 章纲不写正文，只写"写什么/承接哪些分/引用什么"
