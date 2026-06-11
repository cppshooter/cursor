---
name: updater
description: 归档与 RLHF SOP——去 draft 归档、提炼作者反馈写记忆、晋升永久记忆、更新状态
---

# archive-feedback skill

## 流程概览

```text
Step 1: 归档（draft → 定稿）
Step 2: 回填技术部分评分索引表（应答位置/状态）
Step 3: 提炼作者反馈（可复用偏好）
Step 4: 写分类记忆
Step 5: 统计晋升永久记忆
Step 6: 更新状态（status.md / bid.md）
```

## Step 1: 归档

读 `.agent/task/archive-order.md` 确认待归档章节。将通过审查与评分的 `sections/ch-{N}-{slug}.draft.md` 重命名/写入为 `sections/ch-{N}-{slug}.md`（去 draft 后缀），**正文内容不改动**。确认无残留 draft。

> 草稿未通过审查/评分的，拒绝归档，回退 bid-agent。

## Step 2: 回填技术部分评分索引表

打开 `analysis/scoring-checklist.md`（技术部分评分索引表），对本次归档章节承接的每个技术评分点：
- **应答位置**：回填到正文具体小节（如"3.2 安全设计"），形成点对点应答对照索引
- **应答状态**：待应答 → 已定稿

这样在 compose 时，索引表终态可作为附表随技术方案交付，评委据此快速定位每个技术评分点的应答。技术偏离表的应答由 writer 在撰写时完成，updater 仅确认其已逐条应答、无空项。

## Step 3: 提炼作者反馈（RLHF 核心）

从 order 中作者的修改意见提炼**可复用偏好**（会在多章/多轮复现的）。区分：
- ✅ 可复用：文风口径（"应答要先结论后论证"）、参数表述习惯（"统一用'≥'而非'不低于'"）、评分尺度校准（"主观分别给太松"）、结构偏好（"每章开头放评分点对照表"）
- ❌ 一次性：仅本章的具体错别字/单点数据，不沉淀

## Step 4: 写分类记忆（遵循 memory-format-spec.md）

按类别写入 `.claude/memory/`：

| 反馈类别 | 记忆文件 | 相关 agent |
|---------|---------|-----------|
| 撰写/文风/应答口径 | `writing-memory.md` | writer |
| 评分尺度校准 | `scoring-memory.md` | expert |
| 架构偏好 | `architecture-memory.md` | architect |
| 分析/拆点偏好 | `analysis-memory.md` | analyst |

条目格式：
```markdown
## [W-007] 应答先结论后论证
- **触发场景：** 撰写任何评分点应答时
- **规则：** 每个评分点应答首句给明确结论/承诺，再展开论证
- **来源：** 第3轮作者反馈
- **复现次数：** 2
```

## Step 5: 晋升永久记忆

统计各记忆条目"复现次数"，达阈值（默认 ≥3）的晋升到 `.claude/knowledge/permanent-memory.md`（格式同记忆条目），并在原记忆条目标注"已晋升"。永久记忆被各 agent 默认加载。

## Step 6: 更新状态

- `.agent/status.md`：更新 phase、current_chapter、last_archived、rewrite_round、last_score、next_task
- `bid.md`：更新进度索引（已定稿章节清单）

## 验证（Definition of Done）

- [ ] 目标章节已定稿，无 draft 残留
- [ ] 技术部分评分索引表已回填本章应答位置/状态
- [ ] 作者反馈已按类别沉淀（仅可复用项）
- [ ] 达频次条目已晋升 permanent-memory.md
- [ ] status.md / bid.md 进度已更新
- [ ] 记忆条目符合 memory-format-spec.md
