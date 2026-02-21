#!/usr/bin/env python3
"""
validate_skill.py
-----------------
Runs all technical checks on a Claude skill folder before upload.
Reports pass/fail for every rule and exits with code 1 if any check fails.

Usage:
    python validate_skill.py <path-to-skill-folder>

Examples:
    python validate_skill.py ./skills/sprint-planner/
    python validate_skill.py ./my-skill/
"""

import os
import re
import sys
from dataclasses import dataclass, field


# ─── Result model ─────────────────────────────────────────────────────────────

@dataclass
class CheckResult:
    label: str
    passed: bool
    detail: str = ""
    fix: str = ""


# ─── Helpers ──────────────────────────────────────────────────────────────────

GREEN = "\033[92m"
RED   = "\033[91m"
RESET = "\033[0m"
BOLD  = "\033[1m"

def tick(msg: str) -> str:
    return f"{GREEN}✅{RESET}  {msg}"

def cross(msg: str, fix: str = "") -> str:
    line = f"{RED}❌{RESET}  {msg}"
    if fix:
        line += f"\n      {RED}Fix:{RESET} {fix}"
    return line

def is_kebab_case(name: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name))

def word_count(text: str) -> int:
    return len(text.split())

def count_chars_excluding_frontmatter(text: str) -> tuple[str, str]:
    """Split content into frontmatter YAML and body text."""
    if text.startswith("---"):
        # Find the closing --- delimiter
        end = text.find("---", 3)
        if end != -1:
            frontmatter = text[3:end].strip()
            body = text[end + 3:].strip()
            return frontmatter, body
    return "", text


# ─── Checks ───────────────────────────────────────────────────────────────────

def run_checks(skill_dir: str) -> list[CheckResult]:
    results: list[CheckResult] = []

    skill_dir = os.path.abspath(skill_dir)
    folder_name = os.path.basename(skill_dir)

    # ── 1. Folder exists ──
    if not os.path.isdir(skill_dir):
        results.append(CheckResult(
            label="Skill directory exists",
            passed=False,
            detail=f"'{skill_dir}' is not a directory or does not exist.",
            fix="Check the path and try again."
        ))
        return results  # no point continuing

    results.append(CheckResult("Skill directory exists", True, skill_dir))

    # ── 2. SKILL.md exists (exact case) ──
    entries = os.listdir(skill_dir)
    skill_md_matches = [e for e in entries if e == "SKILL.md"]
    wrong_case = [e for e in entries if e.lower() == "skill.md" and e != "SKILL.md"]

    if skill_md_matches:
        results.append(CheckResult("SKILL.md found (exact case)", True))
    else:
        detail = f"Found '{wrong_case[0]}' instead." if wrong_case else "SKILL.md not found."
        results.append(CheckResult(
            "SKILL.md found (exact case)", False,
            detail=detail,
            fix="Rename the file to exactly 'SKILL.md' (case-sensitive)."
        ))
        return results  # can't check content without the file

    skill_md_path = os.path.join(skill_dir, "SKILL.md")
    with open(skill_md_path, "r", encoding="utf-8") as f:
        raw = f.read()

    frontmatter_raw, body = count_chars_excluding_frontmatter(raw)

    # ── 3. No README.md inside folder ──
    has_readme = any(e.lower() == "readme.md" for e in entries)
    results.append(CheckResult(
        "No README.md inside skill folder",
        not has_readme,
        fix="Remove README.md from the skill folder. "
            "A repo-level README is fine, but not inside the skill directory."
    ))

    # ── 4. Folder name is kebab-case ──
    folder_ok = is_kebab_case(folder_name)
    results.append(CheckResult(
        f"Folder name is kebab-case: {folder_name}",
        folder_ok,
        fix="Rename the folder using only lowercase letters and hyphens (e.g., 'my-skill')."
    ))

    # ── 5. Frontmatter delimiters present ──
    has_open_delim = raw.lstrip().startswith("---")
    # Check that there's a closing --- after the opening one
    closing_match = re.search(r"^---\s*\n(.*?)\n---", raw, re.DOTALL | re.MULTILINE)
    fm_valid = has_open_delim and closing_match is not None
    results.append(CheckResult(
        "YAML frontmatter has --- delimiters",
        fm_valid,
        fix="Wrap your frontmatter with --- at the top and --- on a new line after the fields."
    ))

    # ── Parse name and description from frontmatter ──
    name_match = re.search(r"^name:\s*(.+)$", frontmatter_raw, re.MULTILINE)
    desc_match = re.search(r"^description:\s*(.*(?:\n  .*)*)", frontmatter_raw, re.MULTILINE)

    name_value = name_match.group(1).strip().strip('"\'') if name_match else ""
    # Handle multi-line description (YAML block scalar)
    if desc_match:
        raw_desc = desc_match.group(0)
        # Strip "description:" prefix and clean up YAML block scalar markers
        desc_lines = raw_desc.split("\n")
        cleaned = []
        for line in desc_lines:
            line = line.strip()
            if line.startswith("description:"):
                line = line[len("description:"):].strip().lstrip(">|").strip()
            cleaned.append(line)
        desc_value = " ".join(l for l in cleaned if l)
    else:
        desc_value = ""

    # ── 6. name field is present ──
    results.append(CheckResult(
        "name field is present in frontmatter",
        bool(name_value),
        fix="Add 'name: your-skill-name' to the YAML frontmatter."
    ))

    # ── 7. name is kebab-case ──
    if name_value:
        name_kebab_ok = is_kebab_case(name_value)
        results.append(CheckResult(
            f"name is valid kebab-case: {name_value}",
            name_kebab_ok,
            fix="Use only lowercase letters and hyphens in the name field."
        ))

    # ── 8. name matches folder name ──
    if name_value and folder_ok:
        names_match = (name_value == folder_name)
        results.append(CheckResult(
            f"name field matches folder name ({name_value} == {folder_name})",
            names_match,
            fix=f"Either rename the folder to '{name_value}' or update the name field to '{folder_name}'."
        ))

    # ── 9. name has no reserved keywords ──
    if name_value:
        reserved_found = next(
            (r for r in ("claude", "anthropic") if r in name_value.lower()), None
        )
        results.append(CheckResult(
            "name contains no reserved keywords (claude, anthropic)",
            reserved_found is None,
            fix=f"Remove '{reserved_found}' from the skill name — these are reserved by Anthropic."
        ))

    # ── 10. description field is present ──
    results.append(CheckResult(
        "description field is present",
        bool(desc_value),
        fix="Add a description field to the YAML frontmatter."
    ))

    # ── 11. description length ≤ 1024 chars ──
    if desc_value:
        desc_len = len(desc_value)
        desc_len_ok = desc_len <= 1024
        results.append(CheckResult(
            f"description length: {desc_len} chars (limit: 1024)",
            desc_len_ok,
            fix=f"Shorten the description by {desc_len - 1024} characters."
        ))

    # ── 12. description has no XML tags ──
    if desc_value:
        xml_in_desc = bool(re.search(r"[<>]", desc_value))
        results.append(CheckResult(
            "description contains no XML angle brackets < >",
            not xml_in_desc,
            fix="Remove all < and > characters from the description (security restriction)."
        ))

    # ── 13. description contains trigger signal ──
    if desc_value:
        trigger_signals = ["use when", "use for", "trigger", "activate"]
        has_trigger = any(sig in desc_value.lower() for sig in trigger_signals)
        results.append(CheckResult(
            "description contains trigger signal ('Use when', 'Use for', etc.)",
            has_trigger,
            fix="Add 'Use when user asks to [action]' or similar trigger condition to the description."
        ))

    # ── 14. No XML tags anywhere in the full file ──
    xml_in_body = bool(re.search(r"[<>]", body))
    results.append(CheckResult(
        "No XML angle brackets < > in SKILL.md body",
        not xml_in_body,
        fix="Remove all < and > characters from the skill body (security restriction)."
    ))

    # ── 15. Word count under 5000 ──
    wc = word_count(raw)
    results.append(CheckResult(
        f"Word count: {wc} words (limit: 5000)",
        wc <= 5000,
        fix="Move detailed documentation to a references/ file and link to it from SKILL.md."
    ))

    return results


# ─── Reporter ─────────────────────────────────────────────────────────────────

def print_report(results: list[CheckResult], skill_dir: str) -> int:
    """Print the report and return the count of failures."""
    folder_name = os.path.basename(os.path.abspath(skill_dir))
    print(f"\n{BOLD}Skill Validation Report — {folder_name}{RESET}")
    print("─" * 55)

    failures = 0
    for r in results:
        if r.passed:
            print(tick(r.label) + (f"  ({r.detail})" if r.detail else ""))
        else:
            failures += 1
            msg = r.label
            if r.detail:
                msg += f" — {r.detail}"
            print(cross(msg, r.fix))

    print("─" * 55)
    total = len(results)
    if failures == 0:
        print(f"\n{GREEN}{BOLD}✅  All {total} checks passed. Skill is ready for upload.{RESET}\n")
    else:
        print(
            f"\n{RED}{BOLD}❌  {failures} of {total} checks failed. "
            f"Fix the errors above before uploading.{RESET}\n"
        )
    return failures


# ─── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    skill_dir = sys.argv[1]
    results = run_checks(skill_dir)
    failures = print_report(results, skill_dir)
    sys.exit(1 if failures > 0 else 0)


if __name__ == "__main__":
    main()
