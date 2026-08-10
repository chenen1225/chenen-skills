#!/usr/bin/env bash
#
# gzh-skills 一键安装脚本（macOS / Linux / Windows Git Bash）
#
# 功能：
#   1. 把本目录下所有 gzh-* 技能文件夹复制到目标 Agent 平台的 skills/ 目录
#   2. 自动从 gzh-image/config.example.json 生成 config.json 模板（若尚不存在）
#
# 用法：
#   bash install.sh                      # 默认装到 ~/.workbuddy/skills
#   bash install.sh /path/to/skills      # 指定目标目录
#   bash install.sh D:/skills            # Windows 绝对路径也支持
#
set -euo pipefail

# 脚本自身所在目录（兼容软链 / 不同调用方式）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 目标 skills 目录：优先用第一个参数，否则默认 WorkBuddy
TARGET="${1:-$HOME/.workbuddy/skills}"

echo "▶ gzh-skills 一键安装"
echo "  源目录 : $SCRIPT_DIR"
echo "  目标目录: $TARGET"
echo ""

mkdir -p "$TARGET"

# 只安装 gzh-* 技能目录，自动排除 README / .gitignore / 安装脚本本身
mapfile -t SKILLS < <(find "$SCRIPT_DIR" -maxdepth 1 -mindepth 1 -type d -name 'gzh-*' | sort)

if [ "${#SKILLS[@]}" -eq 0 ]; then
  echo "⚠️  未在 $SCRIPT_DIR 下找到任何 gzh-* 技能目录，请确认脚本位置正确。"
  exit 1
fi

count=0
for d in "${SKILLS[@]}"; do
  name="$(basename "$d")"
  echo "  · 安装 $name"
  # 清理旧版本：优先 rm；若被安全删除机制拦截/失败，则 mv 到隐藏回收位兜底，
  # 保证拷贝不被旧文件干扰，且脚本在任一环境下都能一键跑完
  if [ -e "$TARGET/$name" ]; then
    rm -rf "$TARGET/$name" >/dev/null 2>&1 \
      || mv "$TARGET/$name" "$TARGET/.gzh-trash-$name.$$" >/dev/null 2>&1 \
      || true
  fi
  cp -R "$d" "$TARGET/$name"
  count=$((count + 1))
done

# 生成 config.json 模板（不覆盖已有配置）
EXAMPLE="$TARGET/gzh-image/config.example.json"
CFG="$TARGET/gzh-image/config.json"
if [ -f "$EXAMPLE" ] && [ ! -f "$CFG" ]; then
  cp "$EXAMPLE" "$CFG"
  echo "  · 已生成 gzh-image/config.json 模板，请填入你的 providers / wechat 密钥"
fi

echo ""
echo "✅ 完成：共安装 $count 个技能到 $TARGET"
echo "   下一步：编辑 $CFG 填入图像与微信公众号密钥"
echo "   使用说明：见各技能 SKILL.md 与合集 README"
