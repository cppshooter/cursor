# 章纲格式规范

`chapters/ch-{N}-{slug}.md` 是单章撰写指令，由 bid-agent 依据大纲拆出（或作者调整），writer 据此撰写。

## 标准结构

```markdown
---
chapter: 2
slug: tech-architecture
title: 总体技术方案与技术架构
status: outline   # outline → draft → reviewed → archived
bid_type: software   # software / hardware / integration / service
---

## 承接技术评分点
| 技术评分点 | 分值 | 应答要求 |
|-----------|------|---------|
| 2.1 总体架构合理性 | 8 | 提供架构图+技术论证 |
| 2.2 安全设计 | 6 | 安全设计+合规措施 |

## 本章范围
- 写什么：总体技术方案、技术架构、安全设计
- 不写什么：详细设计（第3章）；商务内容（不写）

## 引用依据
- architecture/overall-design.md、architecture/diagrams/topology.mmd
- 检索素材：retriever 提供（.agent/task/retrieval-result.md，仅技术素材）

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
- 每章承接技术评分点必须来自 scoring-checklist.md（技术部分），可追溯
- 章纲不写正文，只写"写什么/承接哪些技术分/引用什么"
- 不规划商务/资质章节（本系统只写技术方案）
