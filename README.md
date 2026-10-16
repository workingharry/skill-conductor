# Skill Conductor (自主思考與動態技能指揮官)

[![Skills Ecosystem](https://img.shields.io/badge/agent--skills-ready-blue.svg)](https://skills.sh)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An autonomous meta-conductor skill for AI agents (Antigravity, Claude Code, Cursor, Cline, Codex, OpenCode, and others) that dynamically evaluates task direction, risk-first difficulty tiers (Tiers 1~4), and engineering trade-offs (YAGNI vs. Rigor) to orchestrate multi-skill workflows.

---

## 🌟 Features

- **Plan-First Prelude (規劃優先鐵律)**:
  - **`/find-skills`**: Always searches the open skills ecosystem first to avoid reinventing wheels.
  - **`/grill-me`**: Relentless Socratic interview on the decision frontier to clarify requirements and dependencies before implementation.
  - **`domain-modeling`**: Automatically records settled architectural decisions as ADRs and updates the project glossary.
- **Dual-Core Implementation (落地實施主力)**:
  - **`/gemini-web-copilot --task code`**: Leverages million-token long context and deep reasoning for complete, production-grade code generation.
  - **`tdd`**: Enforces the Red-Green-Refactor loop with vertical slicing and seam testing.
  - **`/ponytail full`**: Enforces strict YAGNI, standard library first, zero unrequested abstraction, and minimal clean diffs.
- **Enforceable Guardrails (三大強制防護守衛)**:
  1. **Recursion Guard**: Automatically blocks circular dependency and self-invocation.
  2. **Privacy Gate**: Demands explicit user confirmation and file disclosure before dispatching external web automation.
  3. **Explicit Degradation**: Never fails silently; automatically falls back to local reasoning with clear notification.

---

## 📂 Repository Structure

```text
skill-conductor/
├── SKILL.md                          # Main Skill Specification & Execution SOP
├── README.md                         # Project documentation
├── LICENSE                           # MIT License
├── references/
│   ├── dispatch_matrix.md            # Tier 1~4 decision matrix & chaining protocols
│   └── skills_index.json             # Manifest index of available skills
├── scripts/
│   └── skill_indexer.py              # Automated skill indexing & manifest generator
└── tests/
│   └── test_conductor_guardrails.py  # Guardrail automated test suite
```

---

## 🚀 Quick Install

### Using `npx skills`
```bash
npx skills add https://github.com/workingharry/skill-conductor --skill skill-conductor
```

### ⚡ One-Click Ecosystem Install (一鍵安裝所有核心技能)
自動安裝 `/find-skills`、`/grill-me`、`/grill-with-docs`、`/gemini-web-copilot`、`/agent-browser`、`/ponytail` 等全部配套技能：

#### 🍎 macOS / Linux 一行直裝指令 (Terminal Copy & Paste):
```bash
for s in "https://github.com/vercel-labs/skills|find-skills" "https://github.com/mattpocock/skills|grill-me" "https://github.com/mattpocock/skills|grill-with-docs" "https://github.com/mattpocock/skills|domain-modeling" "https://github.com/mattpocock/skills|tdd" "https://github.com/vercel-labs/agent-browser|agent-browser" "https://github.com/dietrichgebert/ponytail|ponytail"; do IFS="|" read -r url name <<< "$s"; npx -y skills add "$url" --skill "$name" --yes; done; [ ! -d ".agents/skills/gemini-web-copilot" ] && git clone https://github.com/workingharry/gemini-web-copilot.git .agents/skills/gemini-web-copilot
```

或者使用遠端 cURL 腳本執行：
```bash
curl -fsSL https://raw.githubusercontent.com/workingharry/skill-conductor/main/scripts/install-ecosystem.sh | bash
```

#### 🪟 Windows (PowerShell) 一行直裝指令:
```powershell
@("https://github.com/vercel-labs/skills|find-skills", "https://github.com/mattpocock/skills|grill-me", "https://github.com/mattpocock/skills|grill-with-docs", "https://github.com/mattpocock/skills|domain-modeling", "https://github.com/mattpocock/skills|tdd", "https://github.com/vercel-labs/agent-browser|agent-browser", "https://github.com/dietrichgebert/ponytail|ponytail") | ForEach-Object { $s, $k = $_ -split '\|'; npx -y skills add $s --skill $k --yes }; if (-not (Test-Path .agents\skills\gemini-web-copilot)) { git clone https://github.com/workingharry/gemini-web-copilot.git .agents\skills\gemini-web-copilot }
```

### Manual Installation
Copy this repository into your workspace's skill directory:
```bash
# Antigravity / Agent Skills standard path:
git clone https://github.com/workingharry/skill-conductor.git .agents/skills/skill-conductor
```

---

## 🧪 Testing Guardrails

Run the automated test suite:
```bash
python tests/test_conductor_guardrails.py
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
