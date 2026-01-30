# Documentation Update Process (Agent Runbook)

This document captures the exact workflow used to complete a documentation checklist for this repo. Use it as a repeatable procedure for future doc audits.

## Goal
- Take a documentation checklist, validate each item against the current codebase, and close items one-by-one with a clean commit per item.
- Keep the work auditable: minimal scope per commit, clear messages, and an updated checklist at the end.

## Pre-flight
1. **Check working tree**
   ```bash
   git status --porcelain=v1
   ```
   - If there are unrelated changes (or untracked directories like `.idea/`), avoid touching them.
2. **Stash everything** (including untracked) to avoid mixing work.
   ```bash
   git stash push -u -m "stash before documentation checklist work"
   ```
3. **Generate the checklist** (if not already present):
   - Review commit history since the last docs update to spot drift:
     ```bash
     git log -1 --format=fuller -- docs
     git log --format='%h %ad %an %s' --date=short <last-docs-commit>..HEAD
     ```
     Replace `<last-docs-commit>` with the commit hash from the first command.
   - Scan docs and code for drift:
     ```bash
     rg -n "TODO|TBD|FIXME" docs README.md
     rg -n "tool|state|memory|config|run.sh|base_module_web" docs README.md
     ```
   - Inspect key source files to validate doc claims:
     ```bash
     sed -n '1,200p' base_module/app.py
     sed -n '1,200p' base_module/main_interface.py
     sed -n '1,200p' model_module/run.sh
     sed -n '1,200p' memory_module/memory.py
     sed -n '1,200p' tool_module/tool_call.py
     sed -n '1,200p' state_module/state_graph.yaml
     ```
   - Compare the findings against `docs/guide/*`, `docs/reference/*`, `docs/ops/*`, and `README.md`.\n   - Draft `docs/documentation_update_checklist.md` with unchecked items.
4. **Commit the checklist** as its own change.

## Execution Loop (one item at a time)
For each checklist item:
1. **Open the relevant doc(s)** and **verify against code** in the repo.
   - Use `rg` + `sed` to find exact sections.
   - Cross-check source files (e.g., `state_module/`, `memory_module/`, `base_module/`, `tool_module/`).
2. **Edit the doc** to match reality (or explicitly document the gap).
   - If a module is untracked (like `base_module_web/`), label docs as prototype-only and remove claims about routes or schema.
   - Prefer concrete statements like “this is stubbed” with guidance on enabling real behavior.
3. **Update the checklist immediately**:
   - Mark the current item `[x]` in `docs/documentation_update_checklist.md`.
4. **Stage and commit immediately**:
   ```bash
   git add <file> docs/documentation_update_checklist.md
   git commit -m "<focused message>"
   ```
   - Keep each commit small and specific to that checklist item.
4. **Repeat** until all items are addressed.

## Common Fix Patterns Used
- **Prototype-only modules**: mark docs as out-of-tree and remove endpoint/schema claims.
- **Port mismatches**: align OpenWebUI docs with `base_module` API (`:1112`) instead of raw LLM (`:30000`).
- **Tool auth scripts**: mention CWD requirements for relative paths (e.g., `cd tool_module` before running `auth_once.py`).
- **Stub behaviors**: explicitly note placeholders in `state_calendar.py` and how to enable real MCP calls.
- **Memory configuration**: document Mem0 config location (`memory_module/memory.py`), hard-coded endpoints, and Postgres schema requirements.
- **Embedding service**: call out `http://localhost:4444/v1` dependency or how to change it.
- **Ops TODOs**: defer with a link to the checklist instead of leaving generic TODOs.

## Finalization
1. **Restate mission completion** in the final response once all items are done.
2. **Do not apply the stash** unless asked by the user.

## Suggested Commit Message Pattern
- “Clarify web UI guide as prototype-only”
- “Mark base_module_web runbook as prototype-only”
- “Point OpenWebUI setup at base_module API”
- “Align OpenWebUI deployment plan with base_module”
- “Update tools guide for MCP and auth helper usage”
- “Document calendar tool stub and enablement”
- “Clarify CLI guide env requirements”
- “Note memory limits are not wired”
- “Refresh state/memory reference and Mem0 config”
- “Document conversation_context schema”
- “Note embeddings endpoint requirement”
- “Note web UI guide is prototype-only in audit plan”
- “Defer ops TODOs with checklist reference”
- “Mark documentation checklist complete”

## Guardrails
- Do **not** touch unrelated files (e.g., `.idea/`) unless explicitly instructed.
- Keep all statements aligned to the current code, not intentions.
- If a fact is uncertain, document it as “prototype-only” or “verify in local branch.”
- Prefer ASCII-only edits unless the file already uses Unicode.
