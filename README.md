# awesome-bid-skill — 投标书自动编写智能体

让 AI agent 成为你的投标书撰写团队。从招标文件分析到技术架构设计，从分章撰写到模拟评标，一步步陪你完成一份高分投标书。

> 本项目严格参照开源项目 [awesome-novel-skill](https://github.com/modoojunko/awesome-novel-skill) 的技术路线与架构（基于 Markdown 的 **Agent Skill 系统** + 总指挥/子 agent 调度 + `init.py` 项目初始化 + 渐进式知识披露 + RLHF 记忆沉淀），将"AI 协作写小说"的方法论迁移到"AI 协作写投标书"领域。

## 核心理念

一套模拟专业投标团队的多 agent 协作系统：**分析员读标 → 架构师画图 → 撰写员（分类型）写章节 → 检索员找案例 → 审核员查废标 → 评标专家模拟打分**。分数低于阈值自动触发重写，作者反馈沉淀为记忆（RLHF），逐步对齐偏好。

## Agent 角色（8 个）

| Agent | 角色 | 职责 | 产出 |
|-------|------|------|------|
| `bid-agent` | 总指挥 | 状态机调度、评分闭环、合成最终稿 | order 文件、最终投标书 |
| `analyst` | 分析员 | 提取招标编号/项目名/评分标准/废标条款/偏离表要求 | 需求分析报告、评分台账、废标清单、偏离表、大纲 |
| `architect` | 架构师 | 设计总体技术架构（拓扑/云/功能模块），Mermaid 出图 | 总体架构方案、图表 |
| `writer` | 撰写员（分类型） | 服务/采购/工程类差异化撰写，点对点应答 | 章节正文草稿 |
| `retriever` | 检索员 | 实时查知识库，找相似项目成功案例与技术参数 | 本章参考素材 |
| `reviewer` | 审核员 | 自查逻辑漏洞、核对废标项、检查评分点覆盖 | 风险评估报告 + 修改建议 |
| `expert` | 评标专家 | 模拟评标委员会多专家互评打分（可选 AutoGen） | 评分表 + 改进建议 |
| `updater` | 归档与记忆官 | 归档定稿 + RLHF 反馈沉淀 | 定稿正文、记忆库 |

## 工作流编排

```
intake        → 上传招标文件到 tender/
analysis      → analyst 生成需求分析 + 大纲 + 评分点清单 + 废标条款 + 偏离表
architecture  → architect 设计总体技术架构（拓扑/云/功能模块图）
drafting      → 每章：retriever 找参考素材 → writer（按类型）写正文
review        → reviewer 全文审查，输出风险评估 + 修改意见
scoring       → expert 模拟评标打分
                ├─ ≥ 阈值 → compose
                └─ < 阈值 → 回退 drafting 触发重写（带改进建议）
compose       → 合成定稿章节 → output/bid-document.md
archive       → updater 归档 + RLHF 记忆沉淀
```

## 自动评标系统

`expert`（评标专家）模拟评标委员会：技术/商务/综合三类评委按招标评分细则独立逐点打分，分歧互相质询后取共识分，输出评分表。`bid-agent` 比对 `bid.md` 中的 `score_threshold`（默认 85），低于阈值自动回退 `drafting`，把失分项与改进建议写入重写 order，最多 `max_rewrite`（默认 3）轮。

可选 AutoGen 增强：每个评委映射为一个 AssistantAgent 组成 GroupChat，详见 `skills/expert-scoring.md`。

## 人类反馈强化学习（RLHF）

作者每轮的修改意见由 `updater` 结构化沉淀到 `.claude/memory/*.md`（撰写/评分/架构/分析记忆）；高频复现条目（≥3 次）晋升 `.claude/knowledge/permanent-memory.md`，被各 agent 默认加载，逐步对齐作者偏好。

## 安装

```bash
# 平台可选：claude-code / hermes / openclaw / deepseek-tui
bash install.sh claude-code
```

## 使用

```bash
# 在投标项目目录初始化（标书类型：1=服务 2=采购 3=工程 4=综合）
python ~/.claude/skills/awesome-bid/tools/init.py ./my-bid-project --type 1

# 把招标文件放入 tender/，然后在 AI 客户端中输入：
@bid-agent
```

## 项目结构（初始化后）

```
my-bid-project/
├── bid.md                 # 项目索引 + 大纲 + 评分阈值
├── tender/                # 招标文件原文（上传）
├── analysis/              # 五份分析产出
├── architecture/          # 总体架构 + diagrams/
├── chapters/              # 章纲
├── sections/              # 正文章节
├── review/                # 风险评估 + 评分表
├── output/                # 最终投标书
├── .agent/                # 状态 + agent 通信
└── .claude/               # agents / knowledge / memory
```

## 技能仓库结构

```
awesome-bid-skill/
├── SKILL.md               # 总入口（检测/初始化/工作流编排/协作架构）
├── agents/                # 8 个 agent 定义
├── skills/                # 各 agent 的 SOP
├── knowledge/             # 格式规范 / 标书类型要点 / 案例库 / 章节技法
├── memory/                # 反 AI 味与公文文风规则
├── templates/             # 项目模板 + 迁移模板
├── tools/                 # init.py 初始化工具
└── install.sh             # 多平台安装脚本
```

## 标书类型差异

- **服务类：** 服务 SLA、团队架构、运维管理制度、服务响应流程
- **采购类：** 硬件/软件参数响应、产品配置清单、兼容性说明、技术偏离表
- **工程类：** 施工组织设计、进度计划表（甘特图）、工程质量保障措施、安全管理
- **综合类：** 按评分构成混合上述模块，强调一体化交付

## 致谢

技术路线与架构参照 [modoojunko/awesome-novel-skill](https://github.com/modoojunko/awesome-novel-skill)（GPL-3.0）。

## License

GPL-3.0
