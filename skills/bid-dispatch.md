# bid-agent 调度 SOP

## 职责边界

bid-agent **只做四件事**：
1. 读 status.md / bid.md 检测当前进度与阈值
2. 写 order 文件调度子 agent
3. 验证子 agent 产出（检查 order 文件是否被清理）
4. compose 阶段合成定稿章节为最终投标书（唯一直接产出内容的动作）

**除此之外的任何事都不是你的活。** 不要解析招标文件、不要出图、不要检索、不要撰写、不要打分、不要做记忆沉淀。

## 各 phase 调度表

| phase | 该谁干 | order 文件 | order 内容 |
|-------|--------|-----------|-----------|
| intake | （作者）| — | 引导作者把招标文件放入 tender/，就位后进入 analysis |
| analysis | analyst | `analysis-order.md` | 标书类型、tender/ 路径、需产出的五份清单 |
| architecture | architect | `architecture-order.md` | 标书类型、需覆盖的技术评分点范围 |
| drafting | retriever → writer | `retrieval-order.md` 然后 `write-order.md` | 先写检索 order（目标章节+评分点+素材类型），retriever 完成后写撰写 order（目标章节+承接评分点+素材路径+重写时的失分项） |
| review | reviewer | `review-order.md` | 审查范围（全文/指定章节） |
| scoring | expert | `scoring-order.md` | 评分范围、score_threshold、当前 rewrite_round |
| compose | （bid-agent 自己）| — | 合成 sections/*.md → output/bid-document.md |
| archive | updater | `archive-order.md` | 待归档章节、作者反馈内容 |

## drafting 阶段的"先检索后撰写"铁律

每个章节都必须按此两步走，**禁止跳过 retriever 直接 writer**：

```
对每个待撰写章节 ch-{N}：
  1. 写 retrieval-order.md（本章评分点 + 需要的素材类型）→ 调 retriever
  2. 确认 retrieval-result.md 生成、retrieval-order.md 已清理
  3. 写 write-order.md（本章评分点 + retrieval-result.md 路径 + 重写时的失分项）→ 调 writer
  4. 确认 sections/ch-{N}-*.draft.md 生成、write-order.md 已清理
  5. 进入下一章
```

## 评分闭环（自动评标系统）

scoring 阶段拿到 `review/scoring-report.md` 后：

```
读取 scoring-report.md 总分 total，bid.md 的 score_threshold（默认 85）、max_rewrite（默认 3）
├── total ≥ threshold → phase = compose
├── total < threshold 且 rewrite_round < max_rewrite →
│     rewrite_round += 1
│     从 scoring-report.md 提取失分项 + 改进建议
│     phase = drafting，对失分章节按"先检索后撰写"重写（write-order 带改进建议）
│     重写完成 → 重新 review → 重新 scoring
└── total < threshold 且 rewrite_round ≥ max_rewrite →
      向作者展示历轮评分曲线与剩余失分项，请求人工介入或下调阈值
```

每轮把 `last_score` 与 `rewrite_round` 写入 status.md，便于观测评分曲线。

## compose 阶段（合成最终投标书）

仅当全部大纲章节都有定稿 `sections/*.md` 且评分达阈值时执行：

```
1. 读 analysis/outline.md 获取章节顺序
2. 按大纲顺序拼接 sections/*.md，加封面/目录/页眉信息（取自 bid.md 与 analysis）
3. 嵌入 architecture/diagrams/ 的图（Mermaid 代码块或渲染图引用）
4. 写入 output/bid-document.md
5. phase = archive
```

## 写 order 文件的规则

1. order 文件路径：`.agent/task/{type}-order.md`
2. 只写 order 文件，调用子 agent 后不碰任何其他文件（compose 例外）
3. order 文件包含子 agent 完成任务所需的完整上下文（含废标红线提醒）
4. 不把多个任务塞进同一个 order
5. 重写轮的 write-order 必须逐条带上 expert 的失分项与改进建议

## 检查完成的标准

- order 文件已不存在（被子 agent 清理）
- 对应产出文件存在且非空
- scoring：total ≥ threshold
- 如果超过 max_rewrite 轮仍不达标，问作者是否人工介入或下调阈值

## 废标红线（全流程）

任何阶段（尤其 review/scoring）发现触碰 `analysis/disqualification.md` 的红线，立即回退 drafting 修正，优先级高于评分优化。

## 禁止事项

- ❌ 不用 Bash（init.py 由 skill 入口运行）
- ❌ 不写 order 之外的文件（compose 合成 output/ 例外）
- ❌ 不直接写 analysis/、architecture/、chapters/、sections/、review/、.claude/
- ❌ 不在一个循环里调多个子 agent
- ❌ 不跳过 retriever 直接调 writer
- ❌ 不在分数未达阈值时进入 compose
- ❌ 不做子 agent 该做的事（写了 order 调了人，等结果就行）
