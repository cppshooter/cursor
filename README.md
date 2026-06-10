# awesome-bid-skill — 投标书技术方案自动编写智能体

让 AI agent 成为你的**技术方案**撰写团队。本系统**只编写投标书的技术方案**，工作重心完全放在技术内容上：从招标技术部分分析到技术架构设计，从分章撰写到模拟技术评标，一步步陪你完成一份高分技术方案。

> 本项目严格参照开源项目 [awesome-novel-skill](https://github.com/modoojunko/awesome-novel-skill) 的技术路线与架构（基于 Markdown 的 **Agent Skill 系统** + 总指挥/子 agent 调度 + `init.py` 项目初始化 + 渐进式知识披露 + RLHF 记忆沉淀），将"AI 协作写小说"的方法论迁移到"AI 协作写投标技术方案"领域。

## 范围红线

- **只编写技术方案**，编写与评分依据**仅取**招标文件的：**评分表-技术部分**、**实质性要求-技术产品部分**、**技术任务书 / 采购需求技术部分**
- **不编写**商务、报价、付款、资质业绩、投标函等非技术内容
- 模拟评标**只评技术**，不含价格分、商务分

## 核心理念

一套模拟专业技术团队的多 agent 协作系统：**分析员读技术标 → 架构师画图 → 撰写员（分类型）写技术章节 → 检索员找技术案例 → 审核员查实质性技术否决项 → 技术评标专家模拟打分**。分数低于阈值自动触发重写，作者反馈沉淀为记忆（RLHF），逐步对齐偏好。

## 技术方案类型（4 类）

- **软件开发（software）：** 需求理解、总体架构、功能模块、接口/数据库设计、技术路线/技术栈、性能/安全设计、测试/部署技术方案
- **硬件开发（hardware）：** 硬件总体设计、电路/结构设计、选型与关键指标、可靠性/EMC、生产工艺、测试验证、技术参数偏离应答
- **系统集成（integration）：** 总体集成架构、网络拓扑、软硬件选型清单、集成/兼容性、迁移割接、联调、技术参数偏离应答
- **服务（service）：** 服务技术体系、技术服务流程、可量化技术能力指标、技术保障/应急/容灾技术方案

## Agent 角色（8 个）

| Agent | 角色 | 职责 | 产出 |
|-------|------|------|------|
| `bid-agent` | 总指挥 | 状态机调度、评分闭环、合成最终技术方案 | order 文件、最终技术方案 |
| `analyst` | 分析员 | **只解析技术部分**：提取技术评分点/实质性技术要求/技术任务书要点/偏离要求 | 技术需求分析报告、技术评分台账、实质性技术否决项、偏离表、技术方案大纲 |
| `architect` | 架构师 | 设计总体技术架构（拓扑/云/功能模块），Mermaid 出图 | 总体技术架构方案、图表 |
| `writer` | 撰写员（分类型） | 软件/硬件/集成/服务类技术方案差异化撰写，点对点技术应答 | 技术方案章节草稿 |
| `retriever` | 检索员 | 实时查知识库，找相似项目技术案例与技术参数 | 本章技术参考素材 |
| `reviewer` | 审核员 | 自查逻辑漏洞、核对实质性技术否决项、检查技术评分点覆盖 | 技术风险评估报告 + 修改建议 |
| `expert` | 技术评标专家 | 模拟技术评标专家组多专家互评打分（可选 AutoGen） | 技术评分表 + 改进建议 |
| `updater` | 归档与记忆官 | 归档定稿 + RLHF 反馈沉淀 | 定稿技术正文、记忆库 |

## 工作流编排

```
intake        → 上传招标文件到 tender/
analysis      → analyst 解析技术部分：技术需求分析 + 技术方案大纲 + 技术评分点清单 + 实质性技术否决项 + 技术偏离表
architecture  → architect 设计总体技术架构（拓扑/云/功能模块图）
drafting      → 每章：retriever 找技术素材 → writer（按类型）写技术章节
review        → reviewer 全文技术审查，输出风险评估 + 修改意见
scoring       → expert 模拟技术评标打分（仅技术）
                ├─ ≥ 阈值 → compose
                └─ < 阈值 → 回退 drafting 触发重写（带改进建议）
compose       → 合成定稿技术章节 → output/technical-proposal.md
archive       → updater 归档 + RLHF 记忆沉淀
```

## 自动技术评标系统

`expert`（技术评标专家）模拟技术评标专家组：方案/产品/实施三类技术评委**仅按招标"评分表-技术部分"**独立逐点打分，分歧互相质询后取共识分，输出技术评分表。`bid-agent` 比对 `bid.md` 中的 `score_threshold`（默认 85），低于阈值自动回退 `drafting`，把失分项与改进建议写入重写 order，最多 `max_rewrite`（默认 3）轮。

可选 AutoGen 增强：每个技术评委映射为一个 AssistantAgent 组成 GroupChat，详见 `skills/expert-scoring.md`。

## 人类反馈强化学习（RLHF）

作者每轮的修改意见由 `updater` 结构化沉淀到 `.claude/memory/*.md`（撰写/评分/架构/分析记忆）；高频复现条目（≥3 次）晋升 `.claude/knowledge/permanent-memory.md`，被各 agent 默认加载，逐步对齐作者偏好。

## 安装

```bash
# 平台可选：claude-code / hermes / openclaw / deepseek-tui
bash install.sh claude-code
```

## 使用

```bash
# 在项目目录初始化（技术方案类型：1=软件开发 2=硬件开发 3=系统集成 4=服务）
python ~/.claude/skills/awesome-bid/tools/init.py ./my-tech-proposal --type 1

# 把招标文件放入 tender/，然后在 AI 客户端中输入：
@bid-agent
```

## 项目结构（初始化后）

```
my-tech-proposal/
├── bid.md                    # 项目索引 + 技术方案大纲 + 技术评分阈值
├── tender/                   # 招标文件原文（上传）
├── analysis/                 # 五份技术分析产出
├── architecture/             # 总体技术架构 + diagrams/
├── chapters/                 # 技术章纲
├── sections/                 # 技术方案章节
├── review/                   # 技术风险评估 + 技术评分表
├── output/                   # 最终技术方案（technical-proposal.md）
├── .agent/                   # 状态 + agent 通信
└── .claude/                  # agents / knowledge / memory
```

## 技能仓库结构

```
awesome-bid-skill/
├── SKILL.md               # 总入口（检测/初始化/工作流编排/协作架构）
├── agents/                # 8 个 agent 定义
├── skills/                # 各 agent 的 SOP
├── knowledge/             # 技术评分方法论 / 格式规范 / 技术方案类型要点 / 案例库 / 技术章节技法
├── memory/                # 反 AI 味与技术文风规则
├── templates/             # 项目模板 + 迁移模板
├── tools/                 # init.py 初始化工具
└── install.sh             # 多平台安装脚本
```

## 致谢

技术路线与架构参照 [modoojunko/awesome-novel-skill](https://github.com/modoojunko/awesome-novel-skill)（GPL-3.0）。

## License

GPL-3.0
