#!/usr/bin/env python3
"""
awesome-bid-skill 项目初始化工具

用法: python init.py [project-path] [--type <编号>]

从 skill 仓库复制 agent 定义、标书类型知识、案例库、反 AI 规则到用户项目目录，
创建完整的投标书编写项目骨架。

标书类型编号: 1=服务类 2=采购类 3=工程类 4=综合类

不带参数时默认在当前目录初始化。
"""

import sys
import os
import shutil
from pathlib import Path

# 强制 UTF-8 编码，避免 Windows 终端中文乱码
for s in (sys.stdin, sys.stdout, sys.stderr):
    try:
        s.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


BID_TYPES = ["service", "procurement", "engineering", "comprehensive"]
BID_TYPE_CN = {
    "service": "服务类",
    "procurement": "采购类",
    "engineering": "工程类",
    "comprehensive": "综合类",
}

SKILL_HOME = Path(os.environ.get("BID_SKILL_HOME", Path(__file__).parent.parent))

SOURCE_AGENTS = SKILL_HOME / "agents"
SOURCE_SKILLS = SKILL_HOME / "skills"
SOURCE_KNOWLEDGE = SKILL_HOME / "knowledge"
SOURCE_TEMPLATES = SKILL_HOME / "templates"
SOURCE_MEMORY = SKILL_HOME / "memory"
SOURCE_ANTI_AI = SKILL_HOME / "memory" / "anti-ai"
SOURCE_BID_TYPE = SKILL_HOME / "knowledge" / "bid-type"
SOURCE_CASE_LIBRARY = SKILL_HOME / "knowledge" / "case-library"
SOURCE_FORMAT_SPECS = SKILL_HOME / "knowledge" / "format-specs"


def main():
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__.strip())
        return

    if len(sys.argv) >= 2 and not sys.argv[1].startswith("--"):
        project_path = Path(sys.argv[1]).resolve()
    else:
        project_path = Path.cwd()

    # 解析可选参数
    bid_type = None
    if "--type" in sys.argv:
        idx = sys.argv.index("--type")
        if idx + 1 < len(sys.argv):
            try:
                bid_type = BID_TYPES[int(sys.argv[idx + 1]) - 1]
            except (IndexError, ValueError):
                print(f"无效标书类型编号，可选 1-{len(BID_TYPES)}")
                sys.exit(1)

    # 安全检查：禁止在技能仓库目录内初始化
    if (project_path / "SKILL.md").exists() and (project_path / "agents").exists():
        print("错误：当前目录疑似 skill 安装目录（含 SKILL.md + agents/），")
        print("请切换到目标投标项目目录后再执行 init.py。")
        sys.exit(1)

    if project_path.exists():
        print("目录已存在，将在其中创建缺失的文件和目录")
    else:
        project_path.mkdir(parents=True)

    print(f"初始化投标书项目: {project_path}")
    print(f"技能仓库: {SKILL_HOME}")

    # Step 1: 选标书类型
    if bid_type is None:
        bid_type = select_bid_type()
    else:
        print(f"标书类型: {bid_type}（{BID_TYPE_CN[bid_type]}）")

    # Step 2: 创建骨架
    create_skeleton(project_path)

    # Step 3: 部署 agent 定义
    deploy_agents(project_path)

    # Step 4: 按类型继承反 AI 规则（memory → knowledge）
    deploy_anti_ai(project_path, bid_type)

    # Step 5: 按类型继承知识（格式规范 + 类型要点 + 案例库）
    deploy_knowledge(project_path, bid_type)

    # Step 6: 生成 CLAUDE.md
    write_claude_md(project_path)

    # Step 7: 生成 MEMORY.md 索引
    write_memory_index(project_path)

    # Step 8: 初始化撰写记忆文件
    init_memory_files(project_path)

    # Step 9: 初始化状态
    write_status(project_path, bid_type)

    print("\n初始化完成!")
    print(f"项目路径: {project_path}")
    print("把招标文件放入 tender/ 目录，然后输入 @bid-agent 开始编写")


def select_bid_type() -> str:
    """交互式选标书类型"""
    print("\n可选标书类型:")
    for i, t in enumerate(BID_TYPES, 1):
        print(f"  {i}. {t}（{BID_TYPE_CN[t]}）")

    while True:
        try:
            choice = input("\n选择标书类型编号: ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(BID_TYPES):
                return BID_TYPES[idx]
        except ValueError:
            pass
        print("无效选择，请重试")


def create_skeleton(project_path: Path):
    """创建项目目录结构 + 拷贝模板"""
    dirs = [
        "tender",
        "analysis",
        "architecture/diagrams",
        "chapters",
        "sections",
        "review",
        "output",
        ".agent/task",
        ".claude/agents",
        ".claude/knowledge",
        ".claude/memory",
    ]
    for d in dirs:
        (project_path / d).mkdir(parents=True, exist_ok=True)

    # 拷贝模板（跳过 migration/ 与 .gitkeep）
    if SOURCE_TEMPLATES.exists():
        for item in SOURCE_TEMPLATES.rglob("*"):
            if item.is_file() and item.name != ".gitkeep":
                rel_path = item.relative_to(SOURCE_TEMPLATES)
                if rel_path.parts[0] == "migration":
                    continue
                target = project_path / rel_path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)
        print("  ✅ 已拷贝项目模板")


def deploy_agents(project_path: Path):
    """复制所有 agent 定义和 skill 到项目 .claude/agents/ 与 .claude/skills/"""
    target = project_path / ".claude" / "agents"
    count = 0
    if SOURCE_AGENTS.exists():
        for item in SOURCE_AGENTS.glob("*.md"):
            shutil.copy2(item, target / item.name)
            count += 1
    # 同步部署 skills（agent 引用 skills/ 路径）
    skills_target = project_path / ".claude" / "skills"
    skills_target.mkdir(parents=True, exist_ok=True)
    if SOURCE_SKILLS.exists():
        for item in SOURCE_SKILLS.glob("*.md"):
            shutil.copy2(item, skills_target / item.name)
            count += 1
    print(f"  ✅ 已部署 {count} 个 agent/skill 文件")


def deploy_anti_ai(project_path: Path, bid_type: str):
    """按类型合成反 AI 规则到 .claude/knowledge/anti-ai.md"""
    knowledge_dir = project_path / ".claude" / "knowledge"
    parts = ["# 反 AI 味与公文文风规则\n\n[community-defaults]\n"]

    common = SOURCE_ANTI_AI / "common-rules.md"
    if common.exists():
        parts.append(common.read_text(encoding="utf-8"))

    type_rules = SOURCE_ANTI_AI / f"{bid_type}.md"
    if type_rules.exists():
        parts.append(f"\n[community-defaults] 标书类型: {bid_type}\n")
        parts.append(type_rules.read_text(encoding="utf-8"))

    (knowledge_dir / "anti-ai.md").write_text("\n".join(parts), encoding="utf-8")
    print(f"  ✅ 已继承反 AI 规则 (通用 + {bid_type})")


def deploy_knowledge(project_path: Path, bid_type: str):
    """按类型拷贝格式规范 + 类型要点 + 案例库到 .claude/knowledge/"""
    knowledge_dir = project_path / ".claude" / "knowledge"
    count = 0

    # 格式规范全部复制
    if SOURCE_FORMAT_SPECS.exists():
        for f in SOURCE_FORMAT_SPECS.glob("*.md"):
            shutil.copy2(f, knowledge_dir / f.name)
            count += 1

    # 标书类型撰写要点
    type_src = SOURCE_BID_TYPE / f"{bid_type}.md"
    if type_src.exists():
        shutil.copy2(type_src, knowledge_dir / "bid-type.md")
        count += 1
        print(f"  ✅ 已继承标书类型要点 ({bid_type})")

    # 案例库：通用 + 类型
    case_parts = ["# 案例库\n"]
    common_case = SOURCE_CASE_LIBRARY / "common.md"
    if common_case.exists():
        case_parts.append(common_case.read_text(encoding="utf-8"))
    type_case = SOURCE_CASE_LIBRARY / f"{bid_type}.md"
    if type_case.exists():
        case_parts.append("\n" + type_case.read_text(encoding="utf-8"))
    (knowledge_dir / "case-library.md").write_text(
        "\n".join(case_parts), encoding="utf-8"
    )
    count += 1
    print("  ✅ 已继承案例库 (通用 + 类型，示范脱敏，建议导入真实历史标书)")

    # 永久记忆占位
    permanent = knowledge_dir / "permanent-memory.md"
    if not permanent.exists():
        permanent.write_text(
            "# 永久记忆\n\n> 从 .claude/memory/ 晋升的高频条目（≥3 次复现），"
            "由 updater 维护，各 agent 默认加载。\n\n---\n\n## 条目列表\n",
            encoding="utf-8",
        )
        count += 1

    print(f"  ✅ 已继承 {count} 个知识文件")


def write_claude_md(project_path: Path):
    """生成项目根目录的 CLAUDE.md"""
    claude_md = """# {project_name}

## AI 指引

本投标项目的编写流程由 8 个 agent 协作完成，定义在 `.claude/agents/` 下。

**开始编写：** 把招标文件放入 `tender/`，然后输入 `@bid-agent` 进入工作流。

**项目结构：**
- `bid.md` — 项目索引 + 大纲 + 评分阈值配置
- `tender/` — 招标文件原文（作者上传）
- `analysis/` — 需求分析报告、评分台账、废标清单、技术偏离表、大纲
- `architecture/` — 总体技术架构 + 图表
- `chapters/` — 章纲
- `sections/` — 正文章节
- `review/` — 风险评估报告 + 评标专家评分表
- `output/` — 最终合成投标书
- `.agent/` — 状态追踪 + agent 通信
- `.claude/knowledge/` — 评分方法论、格式规范、案例库、反 AI 规则
- `.claude/memory/` — 撰写动态记忆（RLHF：作者反馈沉淀）

**工作流：** intake → analysis → architecture → drafting（检索→撰写）→ review → scoring（低分自动重写）→ compose → archive
"""
    (project_path / "CLAUDE.md").write_text(
        claude_md.format(project_name=project_path.name), encoding="utf-8"
    )


def write_status(project_path: Path, bid_type: str):
    """初始化 .agent/status.md"""
    status = f"""# 项目状态

- **skill_version:** 2.0
- **bid_type:** {bid_type}
- **phase:** intake
- **current_chapter:**
- **rewrite_round:** 0
- **last_score:**
- **last_archived:**
- **next_task:** 把招标文件放入 tender/ 目录，确认后由 analyst 解析
"""
    (project_path / ".agent" / "status.md").write_text(status, encoding="utf-8")


def write_memory_index(project_path: Path):
    """生成 .claude/memory/MEMORY.md 占位索引"""
    memory_dir = project_path / ".claude" / "memory"
    (memory_dir / "MEMORY.md").write_text(
        "# 撰写记忆库\n\n（暂无记忆）\n", encoding="utf-8"
    )


MEMORY_FILES = {
    "writing-memory.md": (
        "# 正文撰写记忆\n\n> 记录撰写环节作者的反馈"
        "（文风、应答口径、参数表述、结构偏好）。\n\n**相关 Agent:** writer\n"
        "**相关 Skill:** section-writing\n\n---\n\n## 条目列表\n"
    ),
    "scoring-memory.md": (
        "# 评分尺度记忆\n\n> 记录作者对评标尺度的校准反馈"
        "（主观分松紧、重点关注项）。\n\n**相关 Agent:** expert\n"
        "**相关 Skill:** expert-scoring\n\n---\n\n## 条目列表\n"
    ),
    "architecture-memory.md": (
        "# 架构偏好记忆\n\n> 记录作者对架构选型/出图的偏好。\n\n"
        "**相关 Agent:** architect\n**相关 Skill:** architecture-design\n\n"
        "---\n\n## 条目列表\n"
    ),
    "analysis-memory.md": (
        "# 分析偏好记忆\n\n> 记录作者对评分拆点/大纲的偏好。\n\n"
        "**相关 Agent:** analyst\n**相关 Skill:** requirement-analysis\n\n"
        "---\n\n## 条目列表\n"
    ),
}


def init_memory_files(project_path: Path):
    """初始化 4 个撰写记忆文件"""
    memory_dir = project_path / ".claude" / "memory"
    for filename, content in MEMORY_FILES.items():
        filepath = memory_dir / filename
        if not filepath.exists():
            filepath.write_text(content, encoding="utf-8")
    print("  ✅ 已初始化 4 个撰写记忆文件")


if __name__ == "__main__":
    main()
