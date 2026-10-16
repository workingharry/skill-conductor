#!/usr/bin/env bash
set -e

echo "🚀 [Skill Conductor] 開始一鍵安裝核心技能套件..."

SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/.agents/skills"
mkdir -p "$SKILLS_DIR"

declare -a SKILLS=(
  "https://github.com/vercel-labs/skills|find-skills"
  "https://github.com/mattpocock/skills|grill-me"
  "https://github.com/mattpocock/skills|grill-with-docs"
  "https://github.com/mattpocock/skills|domain-modeling"
  "https://github.com/mattpocock/skills|tdd"
  "https://github.com/mattpocock/skills|codebase-design"
  "https://github.com/mattpocock/skills|improve-codebase-architecture"
  "https://github.com/vercel-labs/agent-browser|agent-browser"
  "https://github.com/dietrichgebert/ponytail|ponytail"
)

for entry in "${SKILLS[@]}"; do
  IFS="|" read -r source skill <<< "$entry"
  echo "📦 正在安裝技能: $skill..."
  npx -y skills add "$source" --skill "$skill" --yes
done

GEMINI_TARGET="$SKILLS_DIR/gemini-web-copilot"
if [ ! -d "$GEMINI_TARGET" ]; then
  echo "📦 正在從 GitHub 安裝 gemini-web-copilot..."
  git clone https://github.com/workingharry/gemini-web-copilot.git "$GEMINI_TARGET"
else
  echo "✅ gemini-web-copilot 已存在，略過 clone。"
fi

echo -e "\n🎉 所有核心技能已全數安裝完成！"
