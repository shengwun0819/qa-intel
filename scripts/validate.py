#!/usr/bin/env python3
"""Static consistency checks for the qa-intel plugin (run locally or in CI)."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []

KNOWLEDGE_PATH = "~/.qa-intel/knowledge/repos/"
# Strings that must not reappear: personal paths and references to logic that does not exist.
FORBIDDEN = ["self_project", "{qa-intel-root}", "~/qa-intel/", "gen-test-cases Phase 0"]


def fail(msg):
    errors.append(msg)


def frontmatter(path):
    m = re.match(r"^---\n(.*?)\n---", path.read_text(encoding="utf-8"), re.DOTALL)
    if not m:
        fail(f"{path.relative_to(ROOT)}: missing frontmatter")
        return {}
    return dict(re.findall(r"^([A-Za-z_-]+):\s*(.*)$", m.group(1), re.MULTILINE))


# plugin.json
try:
    json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
except (OSError, ValueError) as e:
    fail(f"plugin.json invalid: {e}")

# marketplace.json: lists exactly this plugin, with a source that exists
try:
    plugin_name = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["name"]
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    entries = {p.get("name"): p for p in market.get("plugins", [])}
    if plugin_name not in entries:
        fail(f"marketplace.json: no plugin entry named '{plugin_name}' (as in plugin.json)")
    else:
        src = entries[plugin_name].get("source")
        if not isinstance(src, str) or not (ROOT / src).resolve().joinpath(".claude-plugin", "plugin.json").exists():
            fail(f"marketplace.json: source {src!r} does not point at a plugin directory")
except (OSError, ValueError, KeyError) as e:
    fail(f"marketplace.json invalid: {e}")

# skills: <skill>/SKILL.md with name + description, name matches directory
skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
for f in skill_files:
    fm = frontmatter(f)
    for key in ("name", "description"):
        if not fm.get(key):
            fail(f"{f.relative_to(ROOT)}: missing '{key}' in frontmatter")
    if fm.get("name") and fm["name"] != f.parent.name:
        fail(f"{f.relative_to(ROOT)}: name '{fm['name']}' != directory '{f.parent.name}'")

# agents: agents/<name>.md (not agents/<name>/AGENT.md), with name + description + tools
for nested in (ROOT / "agents").glob("*/*"):
    fail(f"{nested.relative_to(ROOT)}: agents must be flat files agents/<name>.md")
for f in sorted((ROOT / "agents").glob("*.md")):
    fm = frontmatter(f)
    for key in ("name", "description", "tools"):
        if not fm.get(key):
            fail(f"{f.relative_to(ROOT)}: missing '{key}' in frontmatter")
    if fm.get("name") and fm["name"] != f.stem:
        fail(f"{f.relative_to(ROOT)}: name '{fm['name']}' != filename '{f.stem}'")
    if "(Tools:" in fm.get("description", ""):
        fail(f"{f.relative_to(ROOT)}: put tools in the 'tools:' field, not in description")

# forbidden strings across skills, agents and docs
scan = list((ROOT / "skills").rglob("*.md")) + list((ROOT / "agents").glob("*.md")) \
    + [ROOT / "README.md", ROOT / "knowledge" / "README.md", ROOT / "docs" / "scenarios.html"]
for f in scan:
    text = f.read_text(encoding="utf-8")
    for bad in FORBIDDEN:
        if bad in text:
            fail(f"{f.relative_to(ROOT)}: contains forbidden string '{bad}'")

# all three skills must agree on the knowledge-base location
for name in ("repo-scout", "risk-analyzer", "gen-test-cases"):
    text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
    if KNOWLEDGE_PATH not in text:
        fail(f"skills/{name}/SKILL.md: does not mention {KNOWLEDGE_PATH}")

# duplicate '### <id>.' headings inside one SKILL.md (e.g. two '2b.')
for f in skill_files:
    seen = {}
    for line in f.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^###\s+(\d+[a-z](?:-[0-9a-z]+)?)\.", line)
        if m:
            if m.group(1) in seen:
                fail(f"{f.relative_to(ROOT)}: duplicate heading id '{m.group(1)}'")
            seen[m.group(1)] = True

# every skill referenced in README / USAGE exists
for doc in ("README.md", "USAGE.md"):
    text = (ROOT / doc).read_text(encoding="utf-8")
    for ref in re.findall(r"`/([a-z-]+)`", text):
        if ref not in {f.parent.name for f in skill_files}:
            fail(f"{doc}: references /{ref} but skills/{ref}/SKILL.md does not exist")

if errors:
    print("\n".join(f"FAIL: {e}" for e in errors))
    sys.exit(1)
print(f"OK: {len(skill_files)} skills, agents and docs consistent")
