# 记忆条目格式规范（RLHF）

updater 把作者反馈沉淀为记忆的统一格式。writer/expert/architect/analyst 加载记忆作为偏好约束，逐步对齐作者。

## 记忆文件分类

| 文件 | 内容 | 加载者 |
|------|------|--------|
| `.claude/memory/writing-memory.md` | 文风、应答口径、参数表述偏好 | writer |
| `.claude/memory/scoring-memory.md` | 评分尺度校准 | expert |
| `.claude/memory/architecture-memory.md` | 架构选型/出图偏好 | architect |
| `.claude/memory/analysis-memory.md` | 拆点/大纲偏好 | analyst |
| `.claude/knowledge/permanent-memory.md` | 高频晋升条目（≥3 次复现） | 全部 agent |

## 条目格式

```markdown
## [W-007] 应答先结论后论证
- **触发场景：** 撰写任何评分点应答时
- **规则：** 每个评分点应答首句给明确结论/承诺，再展开论证
- **来源：** 第3轮作者反馈
- **复现次数：** 2
- **状态：** 活跃 / 已晋升
```

字段说明：
- **编号**：类别前缀（W=writing, S=scoring, A=architecture, N=analysis）+ 序号
- **触发场景**：何时应用此规则
- **规则**：可执行的偏好（命令式表述）
- **来源**：第几轮反馈
- **复现次数**：作者重复表达该偏好的次数，用于晋升判定
- **状态**：活跃 / 已晋升

## 沉淀原则

1. **只记可复用偏好**：会在多章/多轮复现的，不记一次性琐事。
2. **命令式规则**：写成可执行约束（"统一用'≥'"），不写模糊感受。
3. **频次驱动晋升**：复现 ≥3 次晋升永久记忆，被默认加载。
4. **冲突取新**：偏好冲突时以最新作者反馈为准，保留历史条目并标注。
5. **不臆造**：作者未明确表达的偏好不记。
