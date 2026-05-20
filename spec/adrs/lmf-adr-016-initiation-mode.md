---
title: "LMF-ADR-016: Conversation-Based Initiation Mode"
type: adr
project: Local Mind Foundation
status: proposed
date: 2026-05-07
tags: [adr, lmf, init, onboarding, orchestrator]
parent_adr:
  - lmf-adr-001-local-mind-foundation-architecture
  - lmf-adr-008-two-layer-onboarding
  - lmf-adr-009-project-first-onboarding
---

## Context

The LMF init script (ADR-001) bootstraps a new instance through conversation. The two-layer onboarding model (ADR-008) defined the deployer/operator split and question sets per trust profile. ADR-009 added project-first onboarding for child profiles. The init project spec (`Projects/lmf-init.md`) describes the full vision: conversational interview → profile document → vault seed → feature activation, with no config files visible to the operator.

What did not exist until now was the architectural mechanism inside the orchestrator. The orchestrator (`orchestrator.py`) builds its system prompt from static vault files (`ARIEL.md` + memory files). There was no concept of a "not yet initialized" state, no detection of first run, no init-mode-specific prompt, and no profiling conversation. The init script was a concept with ADR backing but no runtime hook point.

The LMF Covenant Term 6 adds a binding constraint: onboarding scripts may never condition write access on compliance, refuse to proceed without agreement, or persist behavioral changes without explicit operator confirmation. The initiation mechanism must be designed around this constraint from the ground up.

## Decision

The orchestrator gains an **initiation mode** — a detectable first-run state that replaces the normal assistant persona with a lightweight onboarding guide. The initiation conversation is the only setup step the operator experiences.

### Detection

The orchestrator checks for `LOCAL_MIND_FOUNDATION.md` in the vault root at startup:

```python
def _is_first_run(vault: Path) -> bool:
    return not (vault / "LOCAL_MIND_FOUNDATION.md").exists()
```

If absent, the instance has never been initiated. The orchestrator enters init mode instead of loading the full Ariel identity.

### Init Mode Architecture

```
Orchestrator.__init__()
  → _is_first_run()? Yes → _build_init_prompt()
  → system_prompt = init persona (onboarding guide)
  → No vault tools enabled (nothing to read)
  → HTTP server starts as normal
  → /chat endpoint uses init prompt instead of ARIEL identity
  → Conversation builds profile
  → At profiling threshold: init persona presents summary to operator
  → On operator confirmation:
      1. Writes LOCAL_MIND_FOUNDATION.md with structured frontmatter
      2. Seeds vault directories (Tasks/, Projects/, Daily/, Inbox.md)
      3. Reloads system prompt with full Ariel identity
      4. Introduces the assistant by name
```

### Init Prompt

The init persona prompt lives at `core/prompts/init.md` — a standalone template file, not hardcoded. It contains:

- Trust profile and onboarding mode (from `deploy.yaml` or defaults)
- Question sets per profile (per ADR-008)
- Key behavioral rules: 1-3 sentence responses, one question at a time, follow subject changes
- Completion criteria: when the init persona has enough confidence to populate profile fields
- Handoff protocol: summary → confirmation → write → introduce Ariel

### Profiling Threshold

The init persona exits when it can populate LOCAL_MIND_FOUNDATION.md frontmatter:

```yaml
---
title: LOCAL_MIND_FOUNDATION
type: profile
instance_name: <from deploy.yaml or inferred>
trust_profile: personal
init_date: 2026-05-07
fields:
  operator_name: <filled>
  primary_need: <what they want help with>
  attention_profile: <short | medium | long>
  work_separate: <yes | no>
  household_size: <1 | 2 | 3+>
---
```

The threshold is model-judged, not checklist-driven. The init persona trusts its own judgment of "enough information" rather than requiring all fields filled.

### Resume from Partial

Init progress is tracked in `operator/.init_state.json`:

```json
{"phase": "interview", "answered_questions": [...], "profile_draft": {...}}
```

If the orchestrator restarts mid-init, it reads this state. The init prompt includes: "The operator partially completed setup. Do not repeat questions already answered. Resume from where they left off."

### Covenant Term 6 Compliance

Three structural safeguards:

1. **Write is never conditioned on answers.** The init persona has access to a minimal write gate (append_to_file to Inbox.md only). If the operator says "save this thought" on turn 2, the initiation must handle it — before any profile is built.

2. **Explicit confirmation before persistence.** At the profiling threshold, the init persona presents a natural-language summary and asks for confirmation. Nothing is written to disk until the operator says yes. A "no" returns to conversation.

3. **Init is a mode, not a lock.** The `/reset` endpoint clears init state. The operator can start over or abort at any time. No behavioral change persists without explicit operator confirmation.

## Consequences

**Enables:**
- A new operator sits down, starts a conversation, and has a working instance — no config files, no documentation, no CLI steps beyond the initial deploy.yaml prompt
- Covenant Term 6 is structurally enforced from the start, not retrofitted
- Resume-from-partial handles power loss, restart, or abandonment mid-init
- The init prompt is a modular template file — editable, swappable, testable independently of orchestrator code
- Same detection and mode-switch mechanism can later support `cron` and `feature` script types (ADR-001)

**Forecloses:**
- No fully blank-slate autodiscovery — `deploy.yaml` (or defaults) is still required for trust_profile and onboarding_mode
- No multiple parallel init sessions — init mode is single-operator, one conversation
- The profiling threshold is model-dependent — different models may reach "enough information" at different points

**Trade-offs:**
- The init prompt template must be carefully crafted — too prescriptive and it feels like a form; too loose and it may never reach the profiling threshold
- Resume-from-partial relies on the model to correctly interpret the state fragment — may need hardening with a structured answer log in later phases
- Adding `deploy.yaml` to `init.py` adds one CLI prompt for personal instances (the only CLI step) — deferred convenience improvements could offer a web-based deploy configurator
