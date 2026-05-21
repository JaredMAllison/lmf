# Domain Experts — Feature Manager Extension

**Date:** 2026-05-12
**Status:** Approved
**Scope:** Option A — schema + registry + seed profile (orchestrator wiring is follow-up)

---

## Problem

LMF needs a way to provide user-agnostic specialist personas to the vault assistant — a Scheduler, a Project Manager, a Vault specialist, a Coach. These domains apply to any LMF instance regardless of who's using it. The Feature Manager already handles installable features; Domain Experts are a new feature type that fits the same pattern.

The goal is to establish the pattern and contract. Specific domains and their prompts are revealed through use, not designed upfront.

---

## Architecture

A `domain-expert` is a Feature Manager feature type with three additions over the base manifest:

1. **`classifier`** — how to route messages to this expert (keywords + description)
2. **`context_template`** — what vault context to load (fixed paths + dynamic query)
3. **`PROMPT.md`** — the specialist's system prompt, stored as a file via `source`

All existing Feature Manager machinery (validate, install, registry, seed profile resolution) is reused without modification except for three targeted additions.

---

## Section 1 — Manifest Schema Extension

File: `features/schema/package-manifest.schema.json`

Changes:
- Add `"domain-expert"` to the `type` enum
- Use `if/then` conditional: when `type` is `domain-expert`, require `classifier` and `context_template`

**`classifier` schema:**
```json
{
  "keywords": ["schedule", "task", "date"],
  "description": "Handles time-based questions and scheduling queries"
}
```
- `keywords`: array of strings, optional — deterministic fast-path routing
- `description`: string, required — used by 7b classifier for ambiguous inputs

**`context_template` schema:**
```json
{
  "paths": ["Tasks/*.md"],
  "query": "{{operator_message}}"
}
```
- `paths`: glob array, optional — always-loaded structural context for this domain
- `query`: string, optional — dynamic Loom search grounded in the operator's message
- Constraint: at least one of `paths` or `query` must be present — enforced via JSON Schema `anyOf`

All other fields (`name`, `version`, `description`, `source`, `install`, `tags`, `trust_level`, `status`) unchanged.

---

## Section 2 — Directory Structure

```
features/
  domain-experts/
    registry.json
    scheduler/
      PROMPT.md
    project-manager/
      PROMPT.md
    vault/
      PROMPT.md
    capture/
      PROMPT.md
    coach/
      PROMPT.md
```

- Each domain expert is a directory under `features/domain-experts/`
- `PROMPT.md` is the only required file by convention — the specialist's full system prompt. Not schema-enforced; the manifest `source` points to the directory, contents are not validated.
- Manifest `source` points to the directory: `{ "path": "{{VAULT_ROOT}}/features/domain-experts/scheduler/" }`
- No other file conventions imposed — future additions (examples, sub-prompts) don't require schema changes
- `{{VAULT_ROOT}}` placeholder resolution already handled by `resolve_placeholders()` in manager.py

---

## Section 3 — Registry File

File: `features/domain-experts/registry.json`

Flat array format identical to `skills/registry.json`. Example entry:

```json
[
  {
    "name": "domain.scheduler",
    "version": "1.0.0",
    "type": "domain-expert",
    "description": "Scheduling specialist — tasks, dates, TTF integration",
    "source": { "path": "{{VAULT_ROOT}}/features/domain-experts/scheduler/" },
    "classifier": {
      "keywords": ["schedule", "task", "date", "appointment", "reminder"],
      "description": "Handles time-based questions, task scheduling, and calendar queries"
    },
    "context_template": {
      "paths": ["Tasks/*.md"],
      "query": "{{operator_message}}"
    },
    "install": [],
    "dependencies": [],
    "trust_level": "Solo",
    "status": "Experimental",
    "tags": ["scheduling", "core"]
  }
]
```

`cmd_validate` in `manager.py` adds `domain-experts/registry.json` to its validation sweep alongside panels and skills — one line addition to `cmd_validate`.

---

## Section 4 — Seed Profile + Init Wizard

**Seed profile** gains `domain_experts` key:

```yaml
domain_experts:
  - domain.scheduler
  - domain.project-manager
  - domain.vault
  - domain.capture
  - domain.coach
```

**`resolve_seed_profile()`** in `manager.py` loads `domain-experts/registry.json` and resolves `domain_experts` name references — same pattern as existing `panels` and `skills` resolution. Minimal addition following the existing loop structure.

**Init wizard** (`init_wizard.py`) gains a new phase after skills:

```
--- Domain Experts ---
Enable default domain experts? [Y/n]:
```

- Yes: writes default set to profile
- No: skips, `domain_experts` key omitted
- No per-expert prompting — list is built through use
- Wizard summary line updated to include domain expert count
- `SEED_TEMPLATE` static template updated with `domain_experts` block

---

## What This Does Not Include (Option B scope)

- Orchestrator routing module
- Runtime classifier logic (keyword match + 7b fallback)
- Context loader implementation
- Specialist response generation

These are the follow-up build, informed by installing and using the first domain experts.

---

## Files Changed

| File | Change |
|------|--------|
| `features/schema/package-manifest.schema.json` | Add `domain-expert` type + conditional fields |
| `features/domain-experts/registry.json` | New file — domain expert registry |
| `features/domain-experts/scheduler/PROMPT.md` | New file — example domain expert |
| `features/feature_manager/manager.py` | Add registry path constant + 3-line `resolve_seed_profile` + 1-line `cmd_validate` additions |
| `features/feature_manager/init_wizard.py` | New wizard phase + seed template update |
