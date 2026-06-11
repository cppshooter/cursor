---
name: awesome-bid
description: 和 AI 协作编写投标书"技术方案"的工作流系统。8 个 agent 协作完成从招标技术部分分析、技术架构设计、分章撰写、技术素材检索、技术风险审核到模拟技术评标的完整流程。入口检测 → 初始化/迁移 → 交 bid-agent 调度。仅基于招标文件的"评分表-技术部分""实质性要求-技术产品部分""技术任务书/采购需求技术部分"编写，不涉及商务。适用：软件开发/硬件开发/系统集成/服务类技术方案。
---

# Bid — 投标书技术方案自动编写工作流

和 AI 一起写投标书的**技术方案**。本系统**只编写技术方案**，工作重心完全放在技术内容上：编写依据仅取招标文件的 **评分表-技术部分**、**实质性要求-技术产品部分**、**技术任务书 / 采购需求技术部分**；**不处理商务、报价、付款、资质业绩等非技术内容**。

本 skill 负责项目状态检测、新项目初始化、旧版项目自动迁移，完成后将控制权交给 bid-agent。

整套系统模拟一个专业技术团队：分析员读技术标、架构师画图、撰写员（分类型）写技术章节、检索员找技术素材、审核员查实质性技术否决项、技术评标专家模拟打分。低于阈值自动触发重写，作者反馈沉淀为记忆（RLHF）。

## 检测流程 — 严格按此执行，禁止跳过

```
检测项目状态
├─ bid.yaml 存在 → 旧版 1.x → 执行自动迁移（见下文）
├─ bid.md 不存在 → 询问作者是否初始化 → 是则执行 init.py
│   └─ python tools/init.py [project-path] [--type <编号>] → 完成后 @bid-agent
└─ bid.md 存在 → 已有项目 → @bid-agent 继续撰写技术方案
```

**强制规则：**
- `bid.md` 不存在时，**先询问作者**是否要在此目录创建技术方案项目，确认后再运行 `init.py`
- 禁止未经确认直接执行 `init.py`
- 确认后必须运行 `init.py`，禁止手动创建目录结构替代
- **禁止在 skill 安装目录（含 `skills/awesome-bid` 路径）内运行 `init.py`**
- `init.py` 执行完毕后，确认 `.agent/status.md` 和 `.claude/agents/` 已生成，方可进入 `@bid-agent`
- 如果 `init.py` 报错，必须先修复问题重新执行，不允许绕过

## 初始化 — 先询问，确认后执行，不可跳过

全新项目先询问作者是否初始化，确认后运行 `init.py`（项目路径可选，默认当前目录）：
```
python tools/init.py [project-path] [--type <编号>]
```

技术方案类型编号：`1=软件开发(software)`、`2=硬件开发(hardware)`、`3=系统集成(integration)`、`4=服务(service)`。

**禁止以任何理由跳过 init.py。**

`init.py` 会：
1. 选技术方案类型（软件开发/硬件开发/系统集成/服务）
2. 创建项目骨架（tender/、analysis/、architecture/、chapters/、sections/、review/、output/）
3. 部署 agent 定义到 `.claude/agents/`
4. 按类型继承反 AI 规则和技术文风到 `.claude/knowledge/`
5. 按类型继承格式规范、技术章节技法、案例库到 `.claude/knowledge/`
6. 创建空白的撰写记忆文件（`.claude/memory/*.md`）
7. 创建永久记忆占位文件（`.claude/knowledge/permanent-memory.md`）
8. 生成 CLAUDE.md
9. 初始化状态文件 `.agent/status.md`

**检查：** 运行后确认 `.agent/status.md` 存在且内容正确，方可进入 `@bid-agent`。

## 招标文件录入 — bid-agent 引导，由 analyst 解析（仅技术部分）

`init.py` 完成后进入 `@bid-agent`，此时 `phase=intake`，按以下流程：

1. **bid-agent 检测到 intake 阶段**，提示作者把招标文件（PDF/Word/纯文本）放入 `tender/` 目录
2. 作者确认文件就位后，bid-agent **写 order 文件** `.agent/task/analysis-order.md`
3. bid-agent 通过 **Agent 工具调用 analyst**
4. **analyst 读取 order + tender/ 原文**，**只解析技术部分**（评分表-技术部分、实质性要求-技术产品部分、技术任务书/采购需求技术部分），输出《技术需求分析报告》《技术方案大纲》《技术评分点清单》《实质性技术否决项》《技术偏离表要求》到 `analysis/`
5. analyst 清理 order 文件并结束
6. **bid-agent 确认 order 已清理**，推进 phase → architecture

**权限规则：** bid-agent 不得直接写 `analysis/` 下的文件，需求解析必须通过 analyst 完成。

## 工作流编排 — 状态机驱动，bid-agent 是唯一调度者

```
intake        → 作者上传招标文件到 tender/
analysis      → analyst 解析技术部分：技术需求分析报告 + 技术方案大纲 + 技术部分评分索引表 + 实质性技术否决项 + 技术偏离表
architecture  → architect 设计总体技术架构（拓扑图/云架构/系统功能模块，Mermaid 出图）
drafting      → 每章：retriever 找技术素材 → writer（按类型）写技术方案章节
review        → reviewer 全文技术审查，输出风险评估报告 + 修改意见，反馈给 writer
scoring       → expert 模拟技术评标专家组打分（仅技术），输出评分表 + 改进建议
                ├─ 分数 ≥ 阈值 → 进入 compose
                └─ 分数 < 阈值 → 回到 drafting 触发重写（带改进建议）
compose       → 合成所有定稿技术章节 + 附"技术部分评分应答索引表"与"技术偏离表"终态 → output/technical-proposal.md
archive       → updater 归档 + 把作者反馈沉淀为记忆（RLHF）
```

**评分闭环（自动技术评标系统）：** scoring 阶段 expert 仅按招标文件的"评分表-技术部分"逐项打分。技术总分低于 `bid.md` 中配置的 `score_threshold`（默认 85）时，bid-agent 自动回退到 drafting，把 expert 的失分项与改进建议写入新一轮 write-order，触发对应技术章节重写。重写次数上限 `max_rewrite`（默认 3 轮），超限则提请作者人工介入。

## 自动迁移（1.x → 2.0）

检测到 `bid.yaml` 存在时，按以下流程自动迁移：

### Step 1: 展示迁移计划
扫描项目目录，给作者看清单（项目元信息 bid.yaml、analysis/、architecture/、chapters/、sections/、review/）。废弃清理：`drafts/`、`tmp/`、`temp-*.txt`、`.vscode/`。**作者确认后继续。**

### Step 2: 备份旧文件
```bash
mkdir -p old
mv bid.yaml analysis/ architecture/ chapters/ sections/ review/ old/
rm -rf drafts/ tmp/ .vscode/
```

### Step 3: 初始化新骨架
```bash
python tools/init.py [project-path] [--type <编号>]
```

### Step 4: 迁移数据（对照 templates/migration/ 字段映射，逐文件转换）
| 优先级 | 旧文件 → 新文件 | 参考模板 |
|--------|----------------|---------|
| P0 | `old/bid.yaml` → `bid.md` | `templates/migration/bid.md.template` |
| P1 | `old/analysis/*.yaml` → `analysis/*.md` | `templates/migration/analysis.md.template` |
| P2 | `old/chapters/*.yaml` → `chapters/ch-{N}.md` | `templates/migration/chapter.md.template` |
| P3 | `old/sections/*.md`（定稿）→ `sections/*.md` | 直接复制，不修改 |

### Step 5: 验收
- [ ] bid.md 存在，skill_version = 2.0
- [ ] analysis/ 五份技术产出齐全
- [ ] chapters/ 章纲数与旧版一致
- [ ] sections/ 技术正文全部复制
- [ ] 旧 .yaml 已移入 old/（无残留）

### Step 6: 交接 bid-agent 评估补充
迁移完成后调度 `@bid-agent`，由其扫描缺失项，逐项引导对应 agent 补充，全部就绪后进入工作流循环。

## 边界条件

| 场景 | 处理 |
|------|------|
| `bid.yaml` 存在 → `bid.md` 不存在 | 旧版 1.x → 执行自动迁移流程 |
| `bid.md` 存在但 `skill_version` < 2.0 | 待升级 → 执行自动迁移流程 |
| `bid.md` 存在且版本匹配 | 已有项目 → @bid-agent |
| 两者都不存在 | 全新项目 → init.py → @bid-agent |
| `init.py` 不可用 | 手动创建目录结构 + 复制 `templates/` 文件 |
| 检测到未提交的 git 变更 | 提示作者先提交/stash |

## 项目目录结构

```
{project-name}/
├── bid.md                       # ★ 项目索引（项目元信息 + 技术方案大纲 + 技术评分阈值）
├── tender/                      # 招标文件原文（作者上传，只读）
│   └── *.pdf / *.docx / *.md
├── analysis/                    # 分析员产出（仅技术）
│   ├── requirement-analysis.md  # 技术需求分析报告
│   ├── scoring-checklist.md     # ★ 技术部分评分索引表（点对点应答台账，独立成表）
│   ├── disqualification.md      # 实质性技术否决项清单
│   ├── deviation-table.md       # ★ 技术偏离表（独立成表）
│   └── outline.md               # 技术方案大纲
├── architecture/                # 架构师产出
│   ├── overall-design.md        # 总体技术架构方案
│   └── diagrams/                # Mermaid / 图表描述
│       └── *.mmd
├── chapters/                    # ★ 技术章纲（status: outline → draft → reviewed → archived）
│   └── ch-{N}-{slug}.md
├── sections/                    # 技术方案章节
│   ├── *.draft.md               # 草稿
│   └── *.md                     # 定稿
├── review/                      # 审核 + 评标产出（仅技术）
│   ├── risk-assessment.md       # 技术风险评估报告
│   └── scoring-report.md        # 技术评标评分表 + 改进建议
├── output/
│   └── technical-proposal.md    # ★ 最终合成技术方案
├── .agent/
│   ├── status.md                # 进度追踪
│   └── task/                    # agent 间 order 文件
└── .claude/
    ├── agents/                  # Agent 定义
    ├── knowledge/               # 技术评分方法论、格式规范、案例库、技术章节技法、反 AI 规则
    └── memory/                  # 撰写动态记忆（RLHF：作者反馈沉淀）
```

## Agent 协作架构

```
bid-agent（总指挥）
  ├─ intake       → 引导作者上传招标文件
  ├─ analysis     → 调度 analyst（技术需求分析 + 大纲 + 技术评分清单 + 实质性技术否决项 + 偏离表）
  ├─ architecture → 调度 architect（总体技术架构 + 图表）
  ├─ drafting     → 每章先调度 retriever（找技术素材）再调度 writer（写技术章节）
  ├─ review       → 调度 reviewer（技术风险评估 + 修改意见）
  ├─ scoring      → 调度 expert（模拟技术评标打分；低于阈值回退 drafting 重写）
  ├─ compose      → 合成定稿技术章节为最终技术方案
  └─ archive      → 调度 updater（归档 + RLHF 记忆沉淀）
```

各 agent 定义在 `agents/`，skill SOP 在 `skills/`。agent 间通过 `.agent/task/*-order.md` 文件通信。

**调度规则：** bid-agent 是唯一调度者，只写 order 文件 + 调用子 agent。所有内容创作（技术分析/架构/章纲/技术正文/检索/审核/评分）、归档更新均由子 agent 完成，bid-agent 不得越权代劳。子 agent 完成任务后清理 order 文件，bid-agent 检测到清理即确认完成。

**重要：bid-agent 是顶层入口，通过 `@bid-agent` 加载进主 agent，禁止通过 Agent 工具将 bid-agent 作为 subagent 调度。**

## 范围红线（全系统）

- **只编写技术方案**，编写与评分依据仅取：评分表-技术部分、实质性要求-技术产品部分、技术任务书/采购需求技术部分
- **不编写**商务、报价、付款、资质业绩、投标函等非技术内容（招标要求在技术方案内附技术性承诺/技术文件的除外）
- expert 评分**只评技术**，不含价格分、商务分

## 两张独立交付表格

系统在 analysis 阶段独立生成、并贯穿全流程维护两张关键表格，最终作为附表随技术方案交付：

| 表格 | 文件 | 生成 | 维护/回填 | 交付 |
|------|------|------|----------|------|
| **技术部分评分索引表** | `analysis/scoring-checklist.md` | analyst 拆评分表-技术部分（评分点→分值→应答要求→承接章节） | updater 归档时回填"应答位置/状态"（依据 writer 正文应答标记）→ 点对点应答对照索引 | compose 作为附表入 technical-proposal.md |
| **技术偏离表** | `analysis/deviation-table.md` | analyst 据技术任务书/实质性要求-技术产品部分生成待应答空表 | writer 逐条应答（正/无/负偏离），reviewer 核对完整性 | compose 作为附表入 technical-proposal.md（硬件/集成类必附） |

## 多技术评委互评与 AutoGen（可选增强）

expert（技术评标专家）默认在单进程内模拟"技术评标专家组"多角色互评（方案评委、产品评委、实施评委各自打分后汇总）。如部署环境具备 AutoGen / 多 agent 编排框架，可将多评委互评映射为 AutoGen 的 GroupChat：每个评委是一个 AssistantAgent，按技术评分细则独立打分并质询彼此分歧，最终由汇总 agent 产出评分表。映射细节见 `skills/expert-scoring.md`。

## 人类反馈强化学习（RLHF）

作者每次对技术章节、评分、架构提出修改意见，updater 在 archive 阶段将其结构化沉淀到 `.claude/memory/*.md`：
- 高频复现的偏好（技术文风、应答口径、参数表述习惯）→ 晋升到 `.claude/knowledge/permanent-memory.md`
- 后续轮次 writer / expert 加载记忆作为约束，逐步对齐作者偏好

记忆条目格式见 `knowledge/format-specs/memory-format-spec.md`。

## 工具契约

| 工具 | 用途 | 谁用 |
|------|------|------|
| **Bash** | 执行 init.py；迁移备份/拷贝命令；Mermaid 渲染（可选） | skill 入口 / architect（出图） |
| **Read** | 读招标技术部分、设定、状态、参考素材 | 所有 agent |
| **Write** | 写 order 文件（bid-agent）；写技术分析/架构/正文/评审/记忆（子 agent） | 各 agent 按权限 |
| **Agent** | bid-agent 调用子 agent | bid-agent 专用 |
| **Edit** | 写 analysis/、architecture/、sections/、review/、.claude/ 下内容文件 | 子 agent（非 bid-agent） |
| **Glob** | 扫描文件 | 所有 agent |
| **Grep** | 检索技术内容、点对点应答比对 | 所有 agent |
