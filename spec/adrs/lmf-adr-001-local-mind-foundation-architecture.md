---
title: "LMF-ADR-001: Local Mind Foundation Architecture"
type: adr
project: Local Mind Foundation
status: accepted
date: 2026-04-17
tags: [adr, lmf, architecture, cognitive-prosthetics]
---

## Context

Over time, three converging threads emerged in the Marlin vault: sociological theory (Legibility from Below series), ND/disability lived experience and advocacy (Building for My People, The High-Resolution Architect), and tool-making (Marlin, TTF, exobrain stack). These aren't parallel projects — they're one thesis expressed in three registers.

No single document held the unifying frame. The cognitive prosthetics stack (Marlin + TTF + exobrain) is a working proof of concept for a broader architecture that could be instanced by anyone who needs it. The "packaged exobrain product" seed (2026-04-17) named the product direction but not the architecture beneath it.

The problem: the architecture was implicit in the implementation. It needed to be named, documented, and separated from any one person's instance so that others could discover and build it.

## Decision

Define **Local Mind Foundation (LMF)** as a named, user-agnostic cognitive prosthetics architecture.

**Core concept:** A self-building cognitive operating system for ND people, structured around a living profile document (`LOCAL_MIND_FOUNDATION.md`) that the LLM interface draws context from, onboards through conversation, and maintains through scheduled and feature-driven review.

**Structure:**

```
LOCAL_MIND_FOUNDATION.md
├── frontmatter fields   ← structured cognitive profile (machine-readable)
├── body                 ← declaration, architecture, active features
└── git history          ← profile evolution over time
```

**Three script types:**

| Script | Trigger | Purpose |
|---|---|---|
| `init` | profile fields are default/empty | Conversational onboarding — fills profile through dialogue, not forms |
| `cron` | calendar interval | Periodic review — "30 days since last check, what's changed?" |
| `feature` | new capability lands | Feature discovery — "does this fit your profile?" |

**Profile is the onboarding artifact.** Configuration happens through conversation, not documentation. The operator talks about their struggles and patterns; the LLM cross-references against available features and fills the profile fields.

**Marlin is the reference instance** — the oldest and most developed instance of this generation. Its implementation details (vault structure, TTF, Ntfy, Gretchen infrastructure) are not part of the universal architecture, but its design decisions inform it.

**The architecture lives above any specific vault** at `~/Documents/LOCAL_MIND_FOUNDATION.md` — not inside Marlin, because Marlin is one instance of it.

**New namespace:** `lmf-adr-NNN` for architectural decisions about LMF as a general architecture, separate from `marlin-adr-NNN` which governs the reference instance.

## Consequences

**Enables:**
- User-agnostic packaging: others can instance the architecture without replicating Jared's specific stack
- Discovery model: features, skills, and adaptations are findable by future users through the init/feature scripts
- Cognitive evolution tracking: git history on the profile document makes change over time legible — itself a prosthetic function for ND memory patterns
- Clear separation between universal architecture (LMF) and reference implementation (Marlin)
- A theoretical foundation (Legibility series + Building for My People) that explains *why* this architecture is needed, not just *how* it works

**Forecloses:**
- Treating Marlin-specific decisions as universal constraints — they must now be clearly labeled as reference-instance choices
- Undocumented growth: new features must be evaluated for LMF vs. instance-level scope before implementation

**Trade-offs:**
- Jared's instance will grow to be the largest and most complex — that complexity must not be mistaken for the baseline. The seed is minimal; the instance is a lifetime of accretion.
- The "cognitive collaborative self-building swiss army knife" metaphor is accurate: each tool is modular, serves a specific executive function, and the combination is comprehensive. But any one user needs only the tools that fit their hand.
