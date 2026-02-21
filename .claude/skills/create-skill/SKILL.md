---
description: Interactive guide to create a Claude skill. Asks targeted questions, builds a valid SKILL.md with correct frontmatter, scaffolds the folder structure, and validates with Python scripts.
---

# Workflow: Create a Claude Skill

Helper scripts (same content, two locations):

- **Antigravity:** `.agent/workflows/scripts/`
- **Claude Code:** `.claude/skills/create-skill/scripts/`

- **`scaffold_skill.py`** — generates the folder structure and a prefilled `SKILL.md` stub.
- **`validate_skill.py`** — runs all 15 technical checks and reports errors before upload.

---

## Entry Point — Choose Your Starting Mode

Before starting, ask the user:

> "Should I start from scratch and guide you through all the questions, or should I analyze our conversation and propose answers based on what we've already been working on?"

- **Mode A — From Scratch:** ask all 7 questions one by one *(default when no prior context)*
- **Mode B — From Context:** infer answers from the conversation, present a proposal, then continue

---

## PHASE 1A — From Scratch (Mode A)

Ask the following questions **one at a time**. Wait for each answer before moving to the next. Offer examples if the user is unsure.

**Q1 — What problem does it solve?**
> "What task do you want Claude to handle with this skill? Describe it in one sentence."
*Goal: understand the desired output and the skill's domain.*

**Q2 — When should it activate?**
> "What phrases would a user type to request this? Give me 3–5 real examples that should trigger the skill."
*Goal: extract trigger phrases for the `description` field — the most important part of the skill.*

**Q3 — What should NOT trigger it?**
> "Are there similar queries that should NOT activate this skill? Is there another skill covering a related case?"
*Goal: define negative triggers to prevent overtriggering. Skip if no overlap risk.*

**Q4 — What tools does it need?**
> "Does the skill need MCP servers, or only Claude's built-in capabilities (read, write, reason, code)?"

- Built-in Claude only → Category 1 or 2
- External services via MCP (Notion, Linear, Slack…) → Category 2 or 3

*If MCP: ask for the exact server name and tool names before writing the SKILL.md — they are case-sensitive and a wrong name breaks the skill silently.*

**Q5 — What is the step-by-step process?**
> "Walk me through how this task would be done manually. List the steps, even if rough."
*Goal: extract the workflow that goes into the SKILL.md body.*

**Q6 — What does a good result look like?**
> "How would you know the skill did its job correctly? What exactly should it produce?"
*Goal: define quality criteria and output examples to embed in the instructions.*

**Q7 — Are there known errors or edge cases?**
> "What could go wrong? Are there special cases the skill should handle differently?"
*Goal: prepare the Troubleshooting section and error handling logic.*

---

## PHASE 1B — From Context (Mode B)

Scan the full conversation history and infer the best possible answer for each of the 7 Phase 1 questions. Then present a single structured proposal — do **not** ask questions one by one. Present everything at once and ask for one confirmation pass.

**Format your proposal exactly like this:**

---
**Proposed skill definition — based on our conversation**

- **Q1 — What it does:** [inferred task and domain]
- **Q2 — Trigger phrases:** [3–5 phrases extracted from how the user has been asking for this work]
- **Q3 — Should NOT trigger:** [out-of-scope cases discussed, or "None identified"]
- **Q4 — Tools needed:** [built-in Claude / MCP server name and tool names if detected]
- **Q5 — Step-by-step process:** [extracted from the workflow built or discussed]
- **Q6 — Success criteria:** [what a good result looks like, based on outputs produced]
- **Q7 — Edge cases / errors:** [issues or exceptions encountered during the conversation]

*Does this look right? Correct anything that's off — then we'll continue to Phase 2.*

---

**Inference rules:**

- Draw from the entire conversation: user messages, tasks completed, outputs produced, errors encountered.
- If an answer cannot be confidently inferred, mark it `[Unknown — please clarify]` and ask only for those gaps.
- **Trigger phrases (Q2) are the most critical** — if you cannot identify at least 3 confidently, ask for them explicitly before continuing.
- If MCP tools were used during the conversation, list their exact names as seen in the tool calls — do not guess.
- Once the user confirms or corrects the proposal, treat those answers as final and proceed to Phase 2 without re-asking anything.

---

## PHASE 2 — Choose Category and Design Pattern

**Skill Category**

| Category | When to use |
|---|---|
| **1 — Document & Asset Creation** | Generates documents, code, or artifacts consistently. No MCP needed. |
| **2 — Workflow Automation** | Multi-step process with logic, validation gates, and possibly multiple tools. |
| **3 — MCP Enhancement** | Adds workflow expertise on top of a connected MCP server. |

**Design Pattern**

| Pattern | When to use |
|---|---|
| **Sequential Workflow** | Linear process with fixed step order and inter-step dependencies. |
| **Multi-MCP Coordination** | Workflow spans multiple external services (e.g., Figma + Drive + Linear). |
| **Iterative Refinement** | Output quality improves through iteration (draft → validate → refine → finalize). |
| **Context-Aware Tool Selection** | Same outcome, different tools depending on context. |
| **Domain-Specific Intelligence** | Embeds specialized knowledge (compliance rules, brand standards, business logic). |

Briefly explain to the user which category and pattern you chose and why. **If unsure between patterns, default to Sequential Workflow** — it is the safest starting point and can be refined later.

---

## PHASE 3 — Write the SKILL.md

### Non-negotiable technical rules

1. **Skill name** — `kebab-case`, no spaces, no capitals, no underscores. Example: `sprint-planner`
2. **Folder name** — identical to the skill name.
3. **File name** — exactly `SKILL.md` (case-sensitive). NOT: `skill.md`, `SKILL.MD`.
4. **No `README.md`** inside the skill folder.
5. **No XML angle brackets** `< >` anywhere in the file.
6. **No "claude" or "anthropic" in the name** — reserved prefixes.

### YAML frontmatter

```yaml
---
name: skill-name-in-kebab-case
description: [WHAT it does] + [WHEN to use it — specific trigger phrases] + [key capabilities]. Max 1024 chars. No XML tags.
# license: MIT                    # include if open-sourcing
# compatibility: Requires MCP server X connected  # 1-500 chars, env requirements
# allowed-tools: "Bash(python:*) WebFetch"  # only if restricting tools
metadata:
  author: [name]
  version: 1.0.0
  category: [productivity | development | design | finance | etc.]
  tags: [tag1, tag2]
---
```

### `description` field rules

- Structure: **[What] + [When — trigger phrases] + [Key capabilities]**
- MUST include exact trigger phrases from Q2.
- Add `Do NOT use for [X].` if overtriggering is a risk.
- Max 1024 characters.

✅ Good: `Manages sprint planning in Linear. Use when user says "plan sprint", "create sprint tasks", or "project planning". Do NOT use for general Linear queries.`
❌ Bad: `Helps with projects.` / `Creates sophisticated documentation.`

### SKILL.md body template

```markdown
# [Skill Name]

[2–3 line intro: what it does and when it activates.]

## Step 1: [First step]
[Actionable instruction. Include exact MCP tool names or script commands.]

## Step 2: [Next step]
[...]

## Validation Gate
CRITICAL: Before [action], verify:
- [Condition 1]
- [Condition 2]

## Examples
**Example 1:** [Scenario]
User says: "[Trigger phrase]"
Actions: 1. [Action 1]  2. [Action 2]
Result: [Expected output]

## Troubleshooting
**Error:** [Symptom] — **Cause:** [Why] — **Solution:** [Fix]
**Error:** [Symptom] — **Cause:** [Why] — **Solution:** [Fix]

## Performance Notes
- Take your time to do this thoroughly
- Quality is more important than speed
- Do not skip validation steps
```

### Instruction writing rules

- Be specific: instead of "validate the data", write `python scripts/validate.py --input {file}`.
- Put critical content first with `## CRITICAL` or `## IMPORTANT` headers.
- Always include `Troubleshooting` (min. 2 cases) and at least 1 full example.
- Keep SKILL.md under 5,000 words — move detailed docs to `references/`.
- For critical validations, use a script instead of language instructions: code is deterministic.

---

## PHASE 4 — Scaffold the Folder Structure

Ask the user:
> "Do we need `scripts/`, `references/`, or `assets/` directories? Or just the `SKILL.md`?"

Map answers to flags: validation/code → `--scripts` | docs/API refs → `--references` | templates/fonts → `--assets`

Then run:

```bash
python .agent/workflows/scripts/scaffold_skill.py \
  --name <skill-name> --author "<name>" --category "<category>" \
  [--scripts] [--references] [--assets] --output <dir>
```

Example:

```bash
python .agent/workflows/scripts/scaffold_skill.py \
  --name sprint-planner --author "David" --category "productivity" \
  --scripts --references --output ./skills
```

Generated structure:

```
skills/sprint-planner/
├── SKILL.md   ← Prefilled stub
├── scripts/
└── references/
```

Open the stub and fill in `description`, steps, examples, and troubleshooting per Phase 3 rules.

---

## PHASE 5 — Review

Show the complete `SKILL.md` to the user and ask:
> "Please review the SKILL.md. Anything to adjust before we move to testing?"

Apply all requested changes. For each `references/` file, create a structured Markdown doc with the relevant information from Phase 1.

---

## PHASE 6 — Testing Plan

### Success Criteria (define before testing)

Per the Anthropic guide — share 1-2 of these with the user before testing: **triggering** (90%+ relevant queries activate the skill), **efficiency** (fewer tool calls and tokens than without the skill), **reliability** (no mid-workflow redirects needed), **consistency** (same request, same structure across sessions).

### Triggering Tests

List queries that SHOULD trigger the skill (min. 5, including paraphrases):
`✅ "[Phrase 1]"` `✅ "[Phrase 2]"` `✅ "[Paraphrase]"` ...

List queries that SHOULD NOT trigger it (min. 3):
`❌ "[Unrelated 1]"` `❌ "[Unrelated 2]"` `❌ "[Edge case]"`

### Functional Tests

For each main use case:

```
Test: [Name] | Given: [Inputs] | When: Skill runs | Then: [Output 1], [Output 2], no errors
```

### Debug tip

Ask Claude: *"When would you use the [skill-name] skill?"* — it quotes the description back. Adjust if context is missing.

---

## PHASE 7 — Automated Validation

Run the validator before declaring the skill ready — code is deterministic, manual review is not:

```bash
python .agent/workflows/scripts/validate_skill.py ./skills/skill-name/
```

The script checks all 15 rules: SKILL.md exact case, no README.md, kebab-case folder, frontmatter delimiters, name validity, name matches folder, no reserved keywords, description present, description ≤1024 chars, no XML tags in description, trigger signal in description, no XML tags in body, word count ≤5000.

Fix every reported error, then **re-run the script** to confirm all checks pass before continuing to Phase 8. Do not proceed on a partial pass.

---

## PHASE 8 — Installation

### Claude.ai

1. Compress `skill-name/` into a `.zip`
2. Go to `Settings > Capabilities > Skills` → **Upload skill**
3. Enable with the toggle

### Claude Code

Place `skill-name/` in Claude Code's skills directory and restart if needed.

**Test:** ask Claude one of the trigger phrases from Phase 6.

---

## Agent Notes

- **Never generate SKILL.md before completing Phase 1.** Questions are essential.
- **Ask questions one at a time.** Wait for each answer.
- If the user dumps info upfront, mentally run Phases 1–2 but still confirm key points before writing files.
- **The `description` field is the most critical part.** A bad description means the skill never activates.
- **Always show the full SKILL.md** and get explicit user confirmation before moving on.
- If the skill uses MCPs, collect the exact server name and tool names during Q4 (Phase 1), before writing any file. Wrong tool names break the skill silently with no error message.
- **Always run `validate_skill.py`.** Trust the script over manual review.
- **Pro tip from Anthropic:** The most effective skill builders iterate on a single challenging task until Claude succeeds in conversation, then extract that winning approach into the skill. This gives faster signal than building broadly from scratch.
- **Skills are living documents.** After the user installs the skill and encounters edge cases, encourage them to return and re-run this workflow with those examples to improve the skill iteratively.
