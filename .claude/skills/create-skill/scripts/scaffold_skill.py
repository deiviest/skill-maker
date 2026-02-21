#!/usr/bin/env python3
"""
scaffold_skill.py
-----------------
Generates a complete Claude skill folder structure with a prefilled SKILL.md stub.

Usage:
    python scaffold_skill.py --name <skill-name> [options]

Options:
    --name          Skill name in kebab-case (required)
    --author        Author name (default: "Unknown")
    --category      Skill category (default: "productivity")
    --tags          Comma-separated tags (default: "")
    --scripts       Include scripts/ directory
    --references    Include references/ directory
    --assets        Include assets/ directory
    --output        Output parent directory (default: current directory)
    --dry-run       Preview the structure without creating files
"""

import argparse
import os
import re
import sys
from datetime import date


# ─── Helpers ──────────────────────────────────────────────────────────────────

def is_kebab_case(name: str) -> bool:
    """Return True if name is valid kebab-case (lowercase letters, digits, hyphens only)."""
    return bool(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name))


def check_reserved(name: str) -> None:
    """Exit with error if name uses reserved prefixes."""
    for reserved in ("claude", "anthropic"):
        if name.startswith(reserved) or f"-{reserved}" in name:
            sys.exit(
                f"[ERROR] Skill name '{name}' contains the reserved keyword '{reserved}'.\n"
                f"        Choose a different name (Anthropic policy)."
            )


def print_tree(base_path: str, paths: list[str]) -> None:
    """Print a simple ASCII tree of the files that will be created."""
    print(f"\n  {os.path.basename(base_path)}/")
    seen_dirs: set[str] = set()
    for p in sorted(paths):
        rel = os.path.relpath(p, base_path)
        parts = rel.split(os.sep)
        # Print any intermediate directories we haven't shown yet
        for depth in range(len(parts) - 1):
            dir_key = os.sep.join(parts[: depth + 1])
            if dir_key not in seen_dirs:
                seen_dirs.add(dir_key)
                indent = "  " + "│   " * depth + "├── "
                print(f"{indent}{parts[depth]}/")
        # Print the file itself
        depth = len(parts) - 1
        indent = "  " + "│   " * depth + "├── "
        print(f"{indent}{parts[-1]}")
    print()


# ─── SKILL.md template ────────────────────────────────────────────────────────

SKILL_MD_TEMPLATE = """\
---
name: {name}
description: >
  [WHAT it does] + [WHEN to use it — include specific trigger phrases users would say].
  Use when user asks to [trigger 1], mentions "[trigger 2]", or says "[trigger 3]".
  Max 1024 characters. No XML angle brackets.

metadata:
  author: {author}
  version: 1.0.0
  category: {category}
  tags: [{tags}]
  created: {today}
---

# {title}

[2–3 line intro: what the skill does and when it activates.]

## Step 1: [First Step]

[Clear, actionable instruction. Mention exact MCP tool names or script paths if applicable.]

## Step 2: [Second Step]

[Continue with the next step in the workflow.]

## Validation Gate

CRITICAL: Before [important action], verify:
- [Condition 1]
- [Condition 2]
- [Condition 3]

## Examples

**Example 1:** [Most common scenario]

User says: "[Exact trigger phrase]"

Actions:
1. [Action 1]
2. [Action 2]

Result: [Expected output]

## Troubleshooting

**Error:** [Common error or symptom]
**Cause:** [Why it happens]
**Solution:** [How to fix it]

**Error:** [Second error case]
**Cause:** [Why it happens]
**Solution:** [How to fix it]

## Performance Notes
- Take your time to do this thoroughly
- Quality is more important than speed
- Do not skip validation steps
"""


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a Claude skill folder with a prefilled SKILL.md stub.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--name", required=True, help="Skill name in kebab-case")
    parser.add_argument("--author", default="Unknown", help="Author name")
    parser.add_argument("--category", default="productivity", help="Skill category")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--scripts", action="store_true", help="Include scripts/ dir")
    parser.add_argument("--references", action="store_true", help="Include references/ dir")
    parser.add_argument("--assets", action="store_true", help="Include assets/ dir")
    parser.add_argument("--output", default=".", help="Output parent directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating files")
    args = parser.parse_args()

    name = args.name.strip()

    # ── Validate name ──
    if not is_kebab_case(name):
        sys.exit(
            f"[ERROR] Skill name '{name}' is not valid kebab-case.\n"
            f"        Use lowercase letters and hyphens only (e.g., 'my-cool-skill')."
        )
    check_reserved(name)

    # ── Build paths ──
    output_dir = os.path.abspath(args.output)
    skill_dir = os.path.join(output_dir, name)
    skill_md = os.path.join(skill_dir, "SKILL.md")

    files_to_create: dict[str, str | None] = {skill_md: None}  # path → content (None = gitkeep)

    if args.scripts:
        files_to_create[os.path.join(skill_dir, "scripts", ".gitkeep")] = None
    if args.references:
        files_to_create[os.path.join(skill_dir, "references", ".gitkeep")] = None
    if args.assets:
        files_to_create[os.path.join(skill_dir, "assets", ".gitkeep")] = None

    # ── Fill SKILL.md ──
    tags_formatted = ", ".join(t.strip() for t in args.tags.split(",") if t.strip())
    title = " ".join(word.capitalize() for word in name.split("-"))
    skill_md_content = SKILL_MD_TEMPLATE.format(
        name=name,
        author=args.author,
        category=args.category,
        tags=tags_formatted,
        today=date.today().isoformat(),
        title=title,
    )
    files_to_create[skill_md] = skill_md_content

    # ── Dry run ──
    if args.dry_run:
        print(f"\n[DRY RUN] The following structure would be created in: {output_dir}")
        print_tree(skill_dir, list(files_to_create.keys()))
        print("  No files were created (--dry-run mode).")
        return

    # ── Check skill dir doesn't already exist ──
    if os.path.exists(skill_dir):
        sys.exit(
            f"[ERROR] Directory already exists: {skill_dir}\n"
            f"        Delete it or choose a different --output path."
        )

    # ── Create files ──
    for path, content in files_to_create.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            if content is not None:
                f.write(content)

    # ── Summary ──
    print(f"\n✅  Skill scaffolded successfully!")
    print(f"    Location: {skill_dir}")
    print_tree(skill_dir, list(files_to_create.keys()))
    print("  Next steps:")
    print(f"  1. Open {skill_md} and fill in the description, steps, and examples.")
    print(f"  2. Run validate_skill.py to check for errors before upload.")
    print(f"  3. Compress the folder and upload to Claude.ai > Settings > Capabilities > Skills.\n")


if __name__ == "__main__":
    main()
