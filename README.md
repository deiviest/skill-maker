# Claude Skill Creator

An interactive, 8-phase workflow that guides you through building a production-ready Claude skill from scratch — with Python scripts for automated scaffolding and validation.

Works with **Antigravity** and **Claude Code**.

---

## Why this exists

Building a Claude skill that reliably activates, follows the right structure, and passes all of Anthropic's technical requirements involves a lot of details. Get the `description` wrong and the skill never triggers. Get the folder name wrong and it won't upload. Miss a frontmatter delimiter and the whole thing breaks.

This workflow encodes all of those rules into a guided process — asking the right questions, generating the files automatically, and validating everything with a script before you ever touch the upload button.

---

## How it works

The workflow has **8 phases**:

| Phase | What happens |
|---|---|
| **1 — Discover** | The agent asks 7 targeted questions: what the skill does, what phrases trigger it, what shouldn't trigger it, what tools it needs, the step-by-step process, what a good result looks like, and known failure cases |
| **2 — Classify** | Determines the right category (Document & Asset Creation / Workflow Automation / MCP Enhancement) and design pattern (Sequential, Multi-MCP, Iterative, Context-Aware, Domain Intelligence) |
| **3 — Write** | Builds `SKILL.md` with correct YAML frontmatter, trigger phrases, workflow steps, examples, error handling, and validation gates |
| **4 — Scaffold** | Runs `scaffold_skill.py` to generate the full folder structure with a prefilled stub |
| **5 — Review** | Shows the complete `SKILL.md` to the user and applies feedback before continuing |
| **6 — Test** | Generates a testing plan: triggering tests (✅ should / ❌ should not), functional tests per use case, and a quick debug tip |
| **7 — Validate** | Runs `validate_skill.py` to check all 15 technical rules programmatically. Must fully pass before proceeding |
| **8 — Install** | Provides exact instructions for uploading to Claude.ai or placing in Claude Code |

---

## What's included

```
.agent/workflows/           ← Antigravity
├── create-skill.md         ← the workflow (invoke with /create-skill)
└── scripts/
    ├── scaffold_skill.py   ← generates the skill folder and SKILL.md stub
    └── validate_skill.py   ← checks 15 technical rules before upload

.claude/workflows/          ← Claude Code (same content)
└── ...
```

---

## Python scripts

Both scripts require **Python 3.10+** with no external dependencies.

### `scaffold_skill.py` — Generate the skill structure

```bash
python .agent/workflows/scripts/scaffold_skill.py \
  --name my-skill \
  --author "Your Name" \
  --category "productivity" \
  --scripts \
  --references \
  --output ./skills
```

**Flags:**

- `--name` — skill name in kebab-case *(required)*
- `--author` — author name for metadata
- `--category` — skill category
- `--scripts` — include a `scripts/` directory
- `--references` — include a `references/` directory
- `--assets` — include an `assets/` directory
- `--output` — parent directory for the generated folder
- `--dry-run` — preview the structure without creating any files

**Output:**

```
skills/my-skill/
├── SKILL.md        ← prefilled stub with frontmatter
├── scripts/
└── references/
```

---

### `validate_skill.py` — Check all rules before upload

```bash
python .agent/workflows/scripts/validate_skill.py ./skills/my-skill/
```

Exits with code `0` if all checks pass, `1` if any fail.

**15 checks it runs:**

| Check | Rule |
|---|---|
| `SKILL.md` exists (exact case) | File naming requirement |
| No `README.md` inside folder | Forbidden file |
| Folder name is kebab-case | Naming convention |
| Frontmatter has `---` delimiters | YAML requirement |
| `name` field is kebab-case | Naming convention |
| `name` matches folder name | Consistency |
| `name` has no reserved keywords | "claude", "anthropic" are reserved |
| `description` field is present | Required field |
| `description` ≤ 1024 characters | Length limit |
| `description` has no XML tags | Security restriction |
| `description` contains trigger signal | Quality requirement |
| No XML tags anywhere in the file | Security restriction |
| Word count ≤ 5000 | Size limit |

**Example output:**

```
Skill Validation Report — my-skill
───────────────────────────────────────────────────────
✅  SKILL.md found (exact case)
✅  No README.md inside skill folder
✅  Folder name is kebab-case: my-skill
✅  YAML frontmatter has --- delimiters
✅  name is valid kebab-case: my-skill
✅  name field matches folder name (my-skill == my-skill)
✅  name contains no reserved keywords (claude, anthropic)
✅  description field is present
✅  description length: 198 chars (limit: 1024)
✅  description contains no XML angle brackets < >
✅  description contains trigger signal ('Use when', 'Use for', etc.)
✅  No XML angle brackets < > in SKILL.md body
✅  Word count: 412 words (limit: 5000)
───────────────────────────────────────────────────────

✅  All 13 checks passed. Skill is ready for upload.
```

---

## Using the workflow

### Antigravity

Type `/create-skill` in your chat.

### Claude Code

Ask: *"Use the create-skill workflow to help me build a skill for [your use case]"*

---

## Installing a finished skill

**Claude.ai:**

1. Compress the skill folder into a `.zip`
2. Go to `Settings > Capabilities > Skills` → **Upload skill**
3. Enable with the toggle

**Claude Code:**
Place the skill folder in Claude Code's skills directory.

---

## Resources

- [Anthropic — The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Skills API Documentation](https://docs.anthropic.com/en/docs/agents-and-tools/skills)
