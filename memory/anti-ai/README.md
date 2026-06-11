# 反 AI 味与技术方案文风规则

技术方案是正式技术文档，最忌"AI 味"与"空话套话"——技术评委一眼识别，主观分掉档。

本目录规则在 `init.py` 时按技术方案类型合成到项目 `.claude/knowledge/anti-ai.md`，由 writer 撰写前加载、reviewer 审查时核对：
- `common-rules.md` — 通用反 AI 味 + 技术文风规则（所有类型继承）
- `software.md` / `hardware.md` / `integration.md` / `service.md` — 各技术类型专属套话防治

核心理念：**用可核验的技术事实、指标、设计、流程说话，删掉一切无信息量的形容词；只写技术，不写商务。**
