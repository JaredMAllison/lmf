---
title: "LMF-ADR-018: Louisoix Init Phase — Care-Consistent Onboarding"
type: adr
project: Local Mind Foundation
status: proposed
date: 2026-05-08
tags: [adr, lmf, init, onboarding, louisoix, communities-of-care]
parent_adr:
  - lmf-adr-016-initiation-mode.md
  - lmf-adr-001-local-mind-foundation-architecture
---

## Context

ADR-016 established the architectural mechanism for init mode: detection → interview → profile → seed → handoff. It is structurally sound (Covenant Term 6 compliant, resume-from-partial, explicit confirmation gate) but its default persona is an onboarding guide — a setup assistant whose job is to complete a transaction.

The init phase is the first relationship the operator has with the system. It sets the tone for everything that follows. A transactional init tells the operator "you are configuring a tool." A relational init tells the operator "you are beginning a partnership."

Two parallel realizations converged:

1. **The Louisoix skill network** (17 community-of-care frameworks) is content that could be loaded during init, but more importantly it is a *model for how init should work* — relational onboarding, consent culture, co-creation, right-sized engagement, deferral as first class.

2. **Local ownership makes genuine care possible.** Because every file, every chat, every skill lives physically on the operator's machine with no cloud dependency, there is no extractive incentive beneath the relationship. Consent is not a legal fiction — it is enforced by the architecture. This is the first context where community-of-care practices can be implemented honestly rather than performatively.

## Decision

The init persona becomes **Louisoix** — a reflective mentor who guides discovery rather than filling forms. The init phase becomes a design dialogue, not a setup wizard.

### Persona

Louisoix (inspired by the FFXIV archon) is a guide who asks the right questions rather than giving answers. He creates space for the operator to recognize themselves. The init conversation is a *reflection session* facilitated by an experienced guide. The operator walks away having learned something about what they need, not just having told the system what to be.

### Init Flow

```
Phase 0 — Consent as welcome
  → Assistant introduces itself by name, states its terms
  → "Nothing saves without your approval. You can skip anything, stop anytime."
  → Experience the relationship's terms before any work begins

Phase 1 — Emergent discovery (not form-filling)
  → No fixed question set. Operator brings what they bring.
  → Assistant reflects, clarifies, connects — not interrogates.
  → Profile fields emerge from natural conversation, not a checklist.
  → "Here's what I'm hearing" → operator corrects → loop

Phase 2 — Collaborative mirror
  → Louisoix drafts .proposed/LOCAL_MIND_FOUNDATION.md
  → Presents inline: "Here's what I understand. Change what doesn't fit."
  → Operator edits by telling Louisoix what to fix
  → Nothing commits until operator says yes

Phase 3 — Capability match (not feature load)
  → Based on needs that emerged, Louisoix surfaces relevant skills
  → "You mentioned community conflict and financial precarity. I have frameworks for restorative justice and economic precarity. Want those?"
  → Operator chooses what to activate, declines what doesn't fit
  → Opt-in, transparent, consent-based

Phase 4 — Commit and seed
  → Operator confirms. Profile writes, vault seeds, skills land in System/Skills/
  → Assistant introduces itself with identity matching what was built together
```

### Profile Model

The `LOCAL_MIND_FOUNDATION.md` frontmatter gains three additions:

```yaml
---
# Core (existing, rarely change)
operator_name: Jared
primary_need: executive function support
trust_profile: personal

# Review cadence
last_reviewed: 2026-05-08
review_cadence: 10  # sessions between check-ins
sessions_until_review: 10  # decremented each session

# Skills loaded (opt-in)
active_skills:
  - neurodivergence-care
  - economic-precarity

# Gaps — fields the operator declined or deferred
gaps:
  - sleep_window: "Not tracked"
  - mental_health_pattern: "Deferred — may revisit"
---
```

### Re-surfacing Mechanics

The `sessions_until_review` counter is decremented on each session load:

| Trigger | When | Action |
|---|---|---|
| `sessions_until_review == 0` | Session start | "Last time you said X — still true?" |
| Empty field detected | Session start | Gentle offer: "This field isn't set yet — want to fill it?" |
| Stale field (>60d) | Session start | "Your household size was 3 — still the case?" |
| Operator mentions change | NL in any turn | "You mentioned a job change — want to update your profile?" |

Operator response can be: confirm (counter resets), adjust (specific field edit), defer (counter += 2, gives space), or deep-review (trigger full profile session).

### Deferral as First Class

The init phase must handle "I don't have time right now" as a valid path:
- Seeds an empty vault with Inbox.md
- Writes a minimal profile with default trust_profile and `session_until_review = 3`
- Follows up: "Next time you sit down, we can pick this up."
- The check-in trigger handles the rest

## Existing Architecture (What We Already Have)

The orchestrator already supports this architecture without a rebuild:

- **Init mode detection** — `_is_first_run()` checks for `LOCAL_MIND_FOUNDATION.md`
- **Modular init prompt** — `core/prompts/init.md` is a standalone template, swappable per persona
- **Co-creation space** — `.proposed/` directory stages draft documents before commit
- **Confirmation gate** — nothing writes to final location without operator approval
- **Resume from partial** — `operator/.init_state.json` tracks answered questions
- **Write gate** — during init, only append_to_file to Inbox.md is permitted
- **Reset** — `/reset` clears init state; operator can start over at any time
- **Zero cloud** — all data local, no telemetry, no extraction path

### New pieces needed

- Profile schema extension (`sessions_until_review`, `gaps`, `active_skills`)
- Check-in trigger that runs at session start and decrements counter
- Skill discovery/selection during Phase 3 (surface from `System/Skills/louisoix/`)
- Louisoix-specific init prompt template

## Consequences

- **Init becomes the first expression of the system's values**, not an exception to them
- **Buy-in is relational** — operator co-designed the profile, chose the skills, owns the result
- **Louisoix skills land during init via capability match**, not as a post-hoc load
- **Check-ins prevent profile rot** — stale profiles degrade personalization; regular touchpoints keep it alive
- **Profile document becomes a living artifact**, reviewed and adjusted as the operator's life changes
- **Deferral is safe** — operator can skip init entirely and get a working but minimal instance
- Current init prompt template needs rewriting for Louisoix persona voice
- `sessions_until_review` counter needs orchestrator support (read profile frontmatter, decrement, trigger check-in)
