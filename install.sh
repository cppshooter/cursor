#!/bin/bash
# Bid Agent Skill 安装脚本
#
# awesome-bid-skill - AI-assisted bid/tender document writing workflow system
# 技术路线参照 awesome-novel-skill（GPL-3.0）的 Agent Skill 架构

set -e

usage() {
    echo "用法: $0 <平台>"
    echo "平台: claude-code, hermes, openclaw, deepseek-tui"
    exit 1
}

if [ $# -lt 1 ]; then
    usage
fi

PLATFORM="$1"

case "$PLATFORM" in
    claude-code)
        SKILLS_DIR="$HOME/.claude/skills"
        ;;
    hermes)
        SKILLS_DIR="$HOME/.hermes/skills"
        ;;
    openclaw)
        SKILLS_DIR="$HOME/.openclaw/skills"
        ;;
    deepseek-tui)
        SKILLS_DIR="$HOME/.deepseek/skills"
        ;;
    *)
        echo "不支持的平台: $PLATFORM"
        usage
        ;;
esac

DEST="$SKILLS_DIR/awesome-bid"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "安装到: $DEST"
export BID_SKILL_HOME="$DEST"

# 将 BID_SKILL_HOME 写入 profile 文件，确保所有 shell 类型可用
for profile_file in "$HOME/.profile" "$HOME/.bashrc"; do
    if ! grep -q "export BID_SKILL_HOME" "$profile_file" 2>/dev/null; then
        echo "export BID_SKILL_HOME=\"$DEST\"" >> "$profile_file"
        echo "已添加 BID_SKILL_HOME=$DEST 到 $profile_file"
    fi
done

# 安全检查：DEST 不能为空、不能是根目录、路径中必须包含 awesome-bid
if [[ -z "$DEST" || "$DEST" == "/" || "$DEST" != *awesome-bid* ]]; then
    echo "错误：安装目标路径异常 ($DEST)，中止。"
    exit 1
fi

# 创建技能目录，已存在则清空
rm -rf "$DEST"
mkdir -p "$DEST"

# 只复制运行时需要的文件
cp "$SCRIPT_DIR/SKILL.md" "$DEST/"
cp -r "$SCRIPT_DIR/agents" "$DEST/"
cp -r "$SCRIPT_DIR/skills" "$DEST/"
cp -r "$SCRIPT_DIR/knowledge" "$DEST/"
cp -r "$SCRIPT_DIR/memory" "$DEST/"
cp -r "$SCRIPT_DIR/templates" "$DEST/"
cp -r "$SCRIPT_DIR/tools" "$DEST/"

echo "安装完成!"
echo "在投标项目目录运行: python \"$DEST/tools/init.py\" [project-path] [--type <1-4>]"
