# Claude Skill Creator Workflow

An interactive workflow for building Claude skills following Anthropic's official best practices. Works in **Antigravity** (`.agent/`) and **Claude Code** (`.claude/`).

---

## What it does

Guides you through the complete skill-building process in 8 structured phases:

1. **Discover** — 7 targeted questions to understand the use case, triggers, tools, and edge cases
2. **Classify** — choose the right category (Document, Workflow, MCP) and design pattern
3. **Write** — build `SKILL.md` with correct frontmatter, trigger phrases, steps, examples, and error handling
4. **Scaffold** — generate the full folder structure automatically with `scaffold_skill.py`
5. **Review** — show the complete `SKILL.md` to the user and apply feedback
6. **Test** — generate triggering tests, functional tests, and a debug tip
7. **Validate** — run `validate_skill.py` to check all 15 technical rules programmatically
8. **Install** — exact steps to upload to Claude.ai or Claude Code

---

## What's included

```
.agent/workflows/          ← for Antigravity users
├── create-skill.md        ← the workflow
└── scripts/
    ├── scaffold_skill.py  ← generates the skill folder structure
    └── validate_skill.py  ← checks all 15 rules before upload

.claude/workflows/         ← for Claude Code users
└── (same structure)
```

---

## Usage

### In Antigravity

Type `/create-skill` in your Antigravity chat.

### In Claude Code

Type `/create-skill` or ask: *"Use the create-skill workflow to help me build a skill for [your use case]"*

---

## Python scripts

Both scripts require **Python 3.10+** and no external dependencies.

### `scaffold_skill.py`

Generates a skill folder with a prefilled `SKILL.md` stub:

```bash
python .agent/workflows/scripts/scaffold_skill.py \
  --name my-skill \
  --author "Your Name" \
  --category "productivity" \
  --scripts --references \
  --output ./skills
```

### `validate_skill.py`

Checks all 15 technical rules and exits with code `1` if any fail:

```bash
python .agent/workflows/scripts/validate_skill.py ./skills/my-skill/
```

Checks include: exact `SKILL.md` casing · kebab-case folder name · frontmatter delimiters · `name` matches folder · no reserved keywords · description ≤ 1024 chars · no XML angle brackets · trigger signal present · word count ≤ 5000

---

## Skills documentation

- [Anthropic Skills Guide](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
