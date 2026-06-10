# 迁移字段映射规范（1.x → 2.0）

旧版以 `bid.yaml` 为索引、各产出为 `.yaml`。新版以 `bid.md` 为索引、Markdown 产出。

## 字段映射

### bid.yaml → bid.md（参考 bid.md.template）
| 旧字段 | 新位置 |
|--------|--------|
| project_name | 标题 + 元信息.项目名称 |
| tender_no | 元信息.招标编号 |
| bid_type | 元信息.标书类型 |
| threshold | 评分闭环配置.score_threshold |

### analysis/*.yaml → analysis/*.md（参考 analysis.md.template）
| 旧字段 | 新位置 |
|--------|--------|
| scoring[] | scoring-checklist.md 台账行 |
| disqualify[] | disqualification.md 行 |
| deviation[] | deviation-table.md 行 |
| outline[] | outline.md 章节 |

### chapters/*.yaml → chapters/ch-{N}.md（参考 chapter.md.template）
| 旧字段 | 新位置 |
|--------|--------|
| chapter / title / status | frontmatter |
| scoring_points[] | 承接评分点表 |

## 原则
- 正文（sections/*.md）只复制定稿，不改内容
- 旧 .yaml 全部移入 old/，验收后由作者删除
