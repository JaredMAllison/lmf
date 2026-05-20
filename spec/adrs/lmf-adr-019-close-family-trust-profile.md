---
title: "LMF-ADR-019: Close Family Trust Profile — Seeded Init"
type: adr
project: Local Mind Foundation
status: proposed
date: 2026-05-09
tags: [adr, lmf, trust, family, init, onboarding]
parent_adr:
  - lmf-adr-006-instance-trust-profiles
  - lmf-adr-016-initiation-mode
  - lmf-adr-018-louisoix-init-phase
---

## Context

The LMF trust profiles (ADR-006) define four relationships: Personal, Work, Child, Household. Each assumes the operator is either setting up for themselves, operating under employer oversight, setting up for a child with parental controls, or co-owning with peers.

None of these fit the pattern of a **Close Family member** — an adult whom the deployer knows well enough to pre-populate their cognitive profile without a ground-zero interview. This pattern is distinct from every existing profile:

| Profile | Who knows the operator? | Init starts from |
|---|---|---|
| Personal | Themselves | Blank conversation |
| Work | Themselves (employer audits) | Blank conversation |
| Child | Parent + child | Parent-guided questions |
| Household | Themselves (shared) | Peer discovery |
| Close Family (new) | Deployer + operator | Deployer's pre-populated seed |

This pattern enables natural word-of-mouth adoption: someone gets value from LMF, sets it up for a family member they understand, and that family member starts from a draft rather than from zero. The deployer's knowledge of the operator is the bridge — trust transfers from the deployer to the system by way of the seed being recognizably accurate.

A seeded init must handle:
- **Confidence gating** — what the deployer knows for certain vs. what they're inferring vs. unknown
- **Consent-first handoff** — the operator sees the seed and confirms/corrects before anything commits
- **No cryptographic enforcement** — this is a consenting adult, not a child or employee
- **Low barrier** — the deployer sets it up, the operator just confirms and starts using it

## Decision

Add a **Close Family trust profile** as the fifth LMF instance profile, with a **seeded init** variant that starts from the deployer's pre-populated knowledge rather than a blank conversation.

### Profile Definition

**Relationship:** Two-person sponsor relationship. The deployer is the seed author and instance sponsor. The family member is the operator. No external third party.

**Enforcement:**
- `tools.config.yaml` path scoping — required (base safety for all instances)
- Ed25519 signing — not required (consenting adult, self-managing)
- AuditLogger — not required
- TransferGate — not required
- Fail-closed chain — not required
- Content policy fields — not required

**Philosophy:** The deployer knows this person well. Trust is established outside the system. The seed is a gift of context, not a constraint. The operator corrects what doesn't fit and owns the result.

### Seeded Init Flow

```
Phase 0 — Deployer seeds the profile
  → Deployer provides what they know:
      - operator_name, relationship, shared_context
      - known_needs (what the deployer thinks would help)
      - known_avoidances (what the deployer knows they'd reject)
      - attention_profile (inferred from lived experience together)
      - household_context (who else lives with them)
      - projects_or_interests (what they care about)
  → Each field is tagged with a confidence:
      high: deployer knows this for certain
      medium: fairly sure but could be wrong
      low: inferring and expects correction
  → Gaps are surfaced: "I don't know [X] about them"

Phase 1 — Operator opens the instance for the first time
  → Assistant introduces itself, explains the setup
  → "[Deployer name] set this up for you. They told me some things
     about you so we don't start from scratch, but you're the one who
     decides what's true. Want to see what they said?"

Phase 2 — Seed review and correction
  → Assistant presents the deployer's seed, field by field
  → Each field shown with the deployer's confidence tag:
      "[Deployer] says you struggle with task memory — that's marked
       as 'high confidence'. Does that fit?"
  → Operator corrects, refines, or confirms each field
  → Where confidence is low, the assistant leads with:
      "[Deployer] wasn't sure about this one. What's actually true?"
  → Where there are gaps: "[Deployer] didn't know [X] about you.
     Want to fill that in, or leave it for now?"

Phase 3 — Profile commit
  → Assistant presents the draft LOCAL_MIND_FOUNDATION.md
  → "Here's what I understand about you. Change what doesn't fit."
  → Operator confirms → profile writes, vault seeds, assistant introduces itself by name

Phase 4 — Capability match
  → Based on confirmed needs, assistant surfaces relevant skills
  → "You mentioned executive function support. I have tools for
     task surfacing and capture. Want those?"
  → Operator opts in or out
```

### Name Display — Opt-In Model

No one is named in the system without their consent. The seed schema includes display-preference fields to enforce this:

- **`seed_author_name_display`** — how the deployer wants to be referred to. `pseudonym` by default. The deployer sets this when they seed the instance.
- **`operator_name_display`** — how the operator wants to be called. `ask` by default — the assistant asks during init.
- The init flow (Phase 1) checks these before using any name. If `ask`, the operator picks their name before anything else appears.
- Public examples in the architecture documentation use generic pseudonyms. Real names only appear with explicit opt-in.

This also enables pseudonyms for cases where: the operator wants privacy from the deployer (unlikely for Close Family but possible), the deployer wants privacy from the public docs, or the operator simply prefers a handle.

### Seed Schema

The seed is a YAML file that the deployer writes before the operator's first session. It lives at `operator/seed.yaml`:

```yaml
# operator/seed.yaml — pre-populated profile seed
seed_author: "Jared"                    # who wrote this — displayed during Phase 2
seed_author_name_display: pseudonym     # real | pseudonym | asked
operator_name: "Jason"
operator_name_display: ask              # real | pseudonym | ask — operator chooses during init
relationship: brother                   # displayed: "[seed_author] ([relationship])"
shared_context: "Shares my neurological profile — AuDHD"

fields:
  primary_need:
    value: "executive function support — task initiation, working memory"
    confidence: high
    source: "Lived experience of shared neurology"

  attention_profile:
    value: "short — rapid context switching, multiple interests"
    confidence: high
    source: "Same profile as mine"

  work_separate:
    value: true
    confidence: medium
    source: "Has a job where focus matters — unsure if they want it in the same system"

  household_size:
    value: 2
    confidence: high
    source: "Knows their living situation"

  avoidances:
    value:
      - "Nagging or guilt-based reminders"
      - "Too many options at once"
      - "Setup requiring technical reading"
    confidence: medium
    source: "General knowledge of personality, not specific to tooling"

  projects_or_interests:
    value:
      - "Star Wars RPG campaign management"
      - "Learning game development (engine TBD)"
    confidence: high
    source: "Direct conversations"

  sleep_window:
    value: "night owl — productive late"
    confidence: low
    source: "Inferring from shared family patterns, not confirmed"
```

### Gaps Detection

The assistant analyzes the seed for fields with no value. These are surfaced during Phase 2 alongside low-confidence fields:

```yaml
gaps:
  - mental_health_pattern: "Not known — surface during review"
  - sensory_sensitivities: "Not known — surface during review"
  - tool_preferences: "Not known — surface during review"
```

### Profile Schema Additions

The `LOCAL_MIND_FOUNDATION.md` frontmatter gains seed metadata:

```yaml
seed:
  author: "Jared"
  date: 2026-05-09
  confidence_summary:
    high: 3
    medium: 4
    low: 1
    gaps: 3
```

### Covenant Term 6 Compliance (Init Mode)

The seeded init inherits all safeguards from ADR-016/018:
- Write is never conditioned on answers (minimal write gate: append_to_file Inbox.md only during init)
- Explicit confirmation before any persistence (Phase 2 field-by-field + Phase 3 full commit)
- Reset available at any time
- Deferral is first class — operator can accept the seed as-is and fill gaps later
- Assistant may not condition continued use on completing all fields

## Consequences

**Enables:**
- Family members get a working instance after confirming a draft, not after a full interview — dramatically lower time-to-value
- The deployer's knowledge of the operator is captured and confidence-tagged, not asserted as fact
- The seed is version-controllable and improvable — each person's seed gets more accurate over time
- Clear architectural pattern for "someone else sets this up for you" without child-brain cryptographic enforcement
- Natural word-of-mouth adoption: deployer trusts LMF → seeds instance for someone they know → operator's trust comes from the deployer, not the system
- Community growth through existing trust networks, not cold discovery

**Forecloses:**
- No blank-slate discovery — the deployer must write the seed. This is appropriate for Close Family but wouldn't work for strangers.
- The seed is only as good as the deployer's knowledge. Low-confidence and gap fields are acknowledged, not hidden.

**Trade-offs:**
- Writing the seed requires the deployer to articulate what they know about someone — this is emotional labor, but far less than a full init interview from the operator's side
- The confidence tagging is human-judged, not algorithmic — deployers must be honest about what they actually know vs. what they're assuming
- The init flow must handle any deployer name in the template — "[deployer] set this up for you" replaces the earlier Jared-specific framing
- Seed quality varies by deployer — a low-quality seed (wrong assumptions, no confidence tagging) could erode trust faster than no seed at all

## Related

- [[lmf-adr-006-instance-trust-profiles]] — parent ADR, enforcement matrix
- [[lmf-adr-016-initiation-mode]] — init mode architecture
- [[lmf-adr-018-louisoix-init-phase]] — relational init persona
- [[LMF — Init Script]] — init project
- [[LMF — Jason Instance]] — first concrete candidate
- [[lmf-design-principles]]
