# Documentation Audit Plan

## Goal
Create a clean documentation-focused branch that starts from the upstream `main` commit `cd512cf17c7d4955e399e619cda840975b1a01da`, review existing docs for accuracy, and update them so new contributors can boot the agent and understand the project layout.

## Git Preparation
1. Ensure your working tree is clean (`git status`). Commit or stash anything pending.
2. Fetch the upstream repository (SGIARK/arkos):
   ```bash
   git remote add upstream https://github.com/SGIARK/arkos.git  # run once
   git fetch upstream
   ```
3. Create the documentation branch from upstream `main`:
   ```bash
   git checkout -b docs/documentation-audit upstream/main
   # or, if you cannot fetch, reset to commit cd512cf17c7d4955e399e619cda840975b1a01da
   ```
4. Verify the branch tip: `git rev-parse HEAD` should report `cd512cf17c7d4955e399e619cda840975b1a01da`.

### Mintlify docs repository (`~/arkos-docs`)
1. Confirm the Mintlify documentation repository is cloned at `~/arkos-docs`.
2. Verify remotes:
   ```bash
   cd ~/arkos-docs
   git remote -v
   ```
   - `origin` should point to `https://github.com/gulkily/arkos-docs` (update with `git remote set-url origin https://github.com/gulkily/arkos-docs` if required).
   - Add `upstream` pointing at the SGIARK canonical repo when you need to sync:
     ```bash
     git remote add upstream https://github.com/SGIARK/arkos-docs.git
     git fetch upstream
     ```
3. Create a companion branch for the audit work:
   ```bash
   git checkout -b docs/documentation-audit upstream/main  # or the default branch name
   ```
4. Track which updates belong in the application repo vs. the Mintlify repo as you progress to keep pull requests focused.

## Audit Checklist
- [x] Inventory all Markdown and text docs (currently `README.md`, `.github` guidelines, and loose notes).
- [x] Compare README dependency list with `requirements.txt` and module imports.
- [x] Validate every command in the README (CLI entry point, inference engine startup, file paths).
- [x] Confirm repository layout matches the directories in tree (`git ls-tree HEAD`).
- [x] Call out missing coverage (e.g., memory persistence, PR guidelines, license summary).
- [x] Identify undocumented code areas (e.g., `agent_module`, `memory_module`, `state_module`, web prototype) and capture required write-ups.
- [x] Record any new docs to author (architecture, deployment, SDK/tooling) for future PRs.
- [x] Propose an information architecture for docs (top-level README, developer guides, deployment runbooks, AI planning docs).
- [x] Review Mintlify site structure (`docs.json`, `introduction.mdx`, `quickstart.mdx`, `/modules`, `/api-reference`) and map each page to corresponding source modules.
- [x] Note any drift between Mintlify content and repository reality; queue updates in the Mintlify repo plan.

### Inventory Snapshot (2025-10-17)
| Area | File / Path | Notes |
| ---- | ----------- | ----- |
| Root | `README.md` | Updated overview, setup, CLI usage. Needs review against dependency list. |
| Root | `FEATURE_DEVELOPMENT_PROCESS.md` | Process doc; confirm if this belongs in `plans/` or operational docs. |
| `.github` | `PULL_REQUEST_GUIDELINES.md`, `PULL_REQUEST_TEMPLATE/pr_template.md` | Up to date; cross-link from Mintlify contribution section. |
| Docs – Guides | `docs/guide/cli_agent.md`, `docs/guide/tools.md`, `docs/guide/web_ui.md` | Populated with current behavior, customization tips, and troubleshooting notes. |
| Docs – Reference | `docs/reference/state_and_memory.md` | Documents state graph, handlers, and memory helper with examples. |
| Docs – Ops | `docs/ops/openwebui_*`, `docs/ops/base_module_web_ubuntu_hosting.md`, `docs/ops/README.md` | Verified existing ops docs moved here. |
| Plans | `plans/ai/*` | Planning documents relocated; add metadata and archive plan states later. |
| Deploy | `deploy/openwebui/README.md` | Consider linking from `docs/ops/`. |
| Tool Module | `tool_module/tool_interface.md` | Candidate for reference doc integration. |

## Update Tasks (initial pass)
- Refresh `README.md` with:
  - Accurate repository description and layout bullet list.
  - Environment setup instructions using `requirements.txt`.
  - Step-by-step guidance for running `model_module/run.sh` and the CLI agent.
  - Notes about memory persistence, tool hooks, and current testing status.
  - Explicit reference to the AGPLv3 license and PR guidelines in `.github/`.
- Document any assumptions or remaining TODOs inside follow-up issues if deeper rewrites are needed (e.g., missing web UI docs).
- Draft outlines for new documentation covering agent internals, state handling, memory persistence, and tool integration.
- Define a docs directory structure (e.g., `docs/guide/`, `docs/reference/`, `docs/ops/`) and note which docs should migrate where. ✅ Implemented (`docs/guide`, `docs/reference`, `docs/ops`, `plans/ai`).
- Plan to move AI development plans into a separate hierarchy (e.g., `plans/ai/`) so top-level docs stay user/developer focused. ✅ Existing planning docs moved under `plans/ai/` with README.
- Prioritize upcoming docs deliverables:
  1. Developer guide for running and extending the CLI agent (`docs/guide/cli_agent.md`).
  2. State and memory reference detailing `state_module` and `memory_module` internals (`docs/reference/state_and_memory.md`).
  3. Tool integration how-to covering `tool_module` patterns (`docs/guide/tools.md`).
  4. Web prototype overview once `base_module_web` stabilizes (`docs/guide/web_ui.md`).
  5. Operations runbooks consolidated under `docs/ops/` (reuse existing OpenWebUI notes once migrated).
- For each deliverable, capture TODO bullets directly in the future doc (even as stubs) so gaps are explicit during the audit. ✅ Draft TODO stubs created in new guide/reference files.
- Lock in target structure before large rewrites: finalize directory map in the plan and ensure follow-up PRs adhere to it. ✅ Directory layout committed above.
- Document Mintlify-specific deliverables:
  1. Align landing pages (`introduction.mdx`, `quickstart.mdx`) with refreshed README messaging. ✅ Completed.
  2. Update module/API pages under `modules/` and `api-reference/` to reflect current code paths and configuration. ✅ Major sections rewritten (base/agent/state/memory/model/tool, architecture, development, testing, API intro, endpoints).
  3. Add cross-links back to in-repo guides where detailed procedures live. ☐ Follow-up: add explicit links once guides stabilize.
  4. Capture any Mintlify component or navigation tweaks required in `docs.json`. ☐ Evaluate once remaining API pages are finalized.

## Validation
1. Re-read updated docs for clarity and ensure commands refer to correct paths.
2. Run `git diff --stat` to spot unintended additions (avoid staging unrelated untracked files).
3. Run `markdownlint` if available; otherwise, visually inspect for formatting issues.
4. When satisfied, stage the changes (`git add README.md docs/documentation_audit_plan.md`) and create a local commit.

## Next Steps
- Open a pull request from `docs/documentation-audit` to upstream `main` once tests pass and reviewers sign off.
- Track any follow-up documentation work (e.g., deployment guides) in separate tickets to keep this PR focused.
