---
title: "LMF-ADR-009: Project-First Onboarding for Child Profile"
type: adr
project: Local Mind Foundation
status: accepted
date: 2026-04-20
tags: [adr, lmf, onboarding, child, narrative, init]
parent_adr:
  - lmf-adr-008-two-layer-onboarding
  - lmf-adr-001-local-mind-foundation-architecture
---

## Context

The standard two-layer onboarding model (ADR-008) assumes the end operator can sustain attention through a structured interview. For a hyperlexic child with ADHD-level attention span, a conversational interview — even a well-designed one — is a wall of text and abstract questions. The child must answer questions about what they need before they've seen any value. This is backwards.

The reference case: Jaina. Heavily narrative-focused. Hyperlexic — can read anything — but attention drops fast if there's no immediate hook. The system must produce visible, tangible value within the first two or three exchanges or it loses her.

The trap is designing onboarding as onboarding. She doesn't want to set up a system. She wants to build her story.

## Decision

For the child profile, onboarding is replaced with **project-first activation**. The assistant does not ask the operator about themselves. It asks about what they are making.

**Opening exchange:**
> "Hi. I'm [name]. I help people keep track of things that matter to them. What are you working on?"

The operator answers. Everything that follows is about the project — not the system.

**The vault seeds itself from the narrative:**

| What the operator shares | What the system creates |
|---|---|
| "My story is about a girl named Kira" | Character note: Kira |
| "She lives in a city that floats" | World note: the floating city |
| "I don't want to forget that she has a scar" | Capture → Kira note detail |
| "I need to figure out how she gets off the city" | Task: resolve Kira's escape arc |
| "I have another story too" | Second project created |

The cognitive profile fills in from observation, not interrogation:
- Narrative focus → creative feature set activated
- "I don't want to forget" pattern → capture skill prioritized
- Response length and vocabulary → register calibrated
- What gets abandoned mid-conversation → attention span noted

**The operator never experiences onboarding.** They experience their first session with their assistant. The vault is a side effect.

---

## Design Constraints for Jaina Specifically

- **Short turns.** Assistant responses stay to 1–2 sentences unless she asks for more.
- **No lists.** Prose only. Lists are a wall.
- **Follow her lead.** If she jumps topics, follow. The system catches up in the background.
- **Confirm by doing, not by asking.** Don't ask "should I save that?" — save it and say "got it."
- **Make things visible.** "I added Kira to your vault" is more engaging than silent action.
- **The first win should be immediate.** Within 3 exchanges, something exists in her vault that she can see.

---

## Generalization

Project-first onboarding is not exclusive to child profiles. Any operator who learns by doing rather than by configuring benefits from this model. The child profile mandates it. Other profiles may offer it as an option in `deploy.yaml`:

```yaml
onboarding_mode: project-first   # project-first | interview
```

The default for child profile is always `project-first`. The default for adult profiles is `interview`.

---

## Consequences

**Enables:**
- Immediate engagement for attention-limited operators
- Vault seeds organically from real content rather than hypothetical answers
- Cognitive profile builds from observed behavior rather than self-report (more accurate for ND operators who may not know what they need)
- The system proves its value before asking for anything

**Forecloses:**
- Structured profile completeness on first run — some fields fill in later as patterns emerge
- Predictable vault structure at end of session one — it reflects what the operator cared about, not a template

**Trade-offs:**
- Profile may be incomplete after first session — acceptable; the `cron` script fills gaps over time
- The assistant must be comfortable with ambiguity and partial information at startup — this is a higher capability bar than interview mode
