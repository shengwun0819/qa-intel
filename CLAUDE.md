# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code **plugin made only of Markdown prompts** — there is no application code, build step or unit-test suite. The three skills (`skills/repo-scout`, `skills/risk-analyzer`, `skills/gen-test-cases`) and one sub-agent (`agents/repo-reader.md`) are instructions that Claude follows at run time. All skill text and user-facing output are in Traditional Chinese; keep new text consistent with that.

It is a personal, portable QA toolkit meant to move between companies, so skills and templates must stay free of company-specific names, paths and conventions.

## Commands

```bash
python3 -I scripts/validate.py        # the only automated check; CI (.github/workflows/validate.yml) runs the same
claude --plugin-dir "$(pwd)"          # load this working copy as a plugin to try a skill by hand
claude plugin validate .              # official manifest check (plugin.json + marketplace.json)
```

The repo is its own single-plugin marketplace (`.claude-plugin/marketplace.json`, `source: "./"`); keep its plugin `name` equal to the one in `plugin.json`. The `CLAUDE.md` warning from `claude plugin validate` is expected: this file is developer guidance for the repo, not context shipped with the plugin.

There is no way to run a skill automatically. Verify skill changes by reading them end to end and, when possible, trying them with `--plugin-dir`.

## Architecture

The skills share state through one file per repo, not through code:

```
/repo-scout ──writes──▶ ~/.qa-intel/knowledge/repos/<repo>.md ◀──reads── /risk-analyzer
                         (QA_INTEL_HOME overrides ~/.qa-intel)  ◀──reads── /gen-test-cases
```

- The knowledge base lives **outside** the plugin directory. All three skills, `knowledge/README.md`, `README.md` and `docs/scenarios.html` must name the same path; `scripts/validate.py` enforces that the path appears in every skill. If you change the path, change it everywhere in one commit.
- `repo-scout` Phase 2 may delegate the reading to the `repo-reader` agent; the agent's output sections must match the "Phase 3" template in `repo-scout`.
- `risk-analyzer` ends with a "建議測試重點" list meant as input to `gen-test-cases`, but `gen-test-cases` Phase 1 has no input source for it yet (the hand-off is still manual).
- `gen-test-cases` has the most branching: Phase 1 collects source and stage (Development vs Verification), Phase 2 gathers context from up to six sources, Phase 3 produces cases using one of three templates in `skills/gen-test-cases/templates/`, Phase 4 writes to a ClickUp Doc or a local file. Planned work is tracked in `skills/gen-test-cases/FUTURE.md`.
- The only PM tool actually implemented is ClickUp (MCP tools `mcp__clickup__clickup_*`, with a REST fallback in `gen-test-cases` Phase 4). Jira and Linear are planned, not supported.

## Conventions enforced by `scripts/validate.py`

- Each skill is `skills/<name>/SKILL.md` with `name` (equal to the directory name) and `description` in frontmatter.
- Agents are flat files `agents/<name>.md` with `name`, `description` and a `tools:` field (not `(Tools: …)` inside the description).
- Step headings inside a `SKILL.md` (`### 2b.`, `### 3d-補.` …) must be unique; other text refers to steps by these ids, so renumbering means updating those references.
- User-facing docs and skill text write commands with the plugin prefix (`/qa-intel:gen-test-cases`), because the user also has `swiss-knife:gen-test-cases` installed and bare names can hit the wrong skill. Skill `description`s say when to defer to a same-named skill from another plugin.
- Forbidden strings: `self_project`, `{qa-intel-root}`, `~/qa-intel/`, `gen-test-cases Phase 0`.

## Documentation vs. reality

`docs/scenarios.html`, `README.md` and `USAGE.md` describe behaviour for users. Keep `USAGE.md` to one page of minimal usage that links to the other two, so there are not three copies of the details to keep in sync. Features that are only planned (`projects/<company>/project.md`, custom templates, bug-record regression cases, Jira/Linear, automatic input detection) must be labelled as planned — do not describe them as working. Never commit real knowledge-base files or company-specific material; `knowledge/` here holds documentation only.
