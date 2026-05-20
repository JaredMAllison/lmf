---
title: "LMF-ADR-005: ADR Inheritance Model"
type: adr
project: Local Mind Foundation
status: accepted
date: 2026-04-20
tags: [adr, lmf, architecture, adr-system]
---

## Context

The LMF architecture produces ADRs at two levels: universal (LMF namespace) and instance-specific (Marlin, Prosper0, Ariel von Marlin, etc.). Instance ADRs were referencing parent LMF ADRs via wiki links, but only informally — no schema field declared the relationship, and no convention existed for navigating from a parent decision down to all the instances that implement it.

The gap: an LMF architectural decision could exist with no visible trail to which instances had adopted, adapted, or ignored it. Over time this makes the architecture hard to audit and harder to propagate changes across.

## Decision

Add a `parent_adr` frontmatter field to instance-level ADRs that implement or are constrained by an LMF decision. The field is optional — not every instance ADR has an LMF parent. When it does, the value is the canonical ADR filename (without `.md`).

**Example:**

```yaml
---
title: "Prosper0-ADR-007: Inference Runtime"
parent_adr: lmf-adr-001-local-mind-foundation-architecture
---
```

Multiple parents are allowed as a YAML list when an instance ADR implements more than one LMF decision.

**Instance ADRs do not replace LMF ADRs.** An instance ADR may narrow, specialize, or extend an LMF decision for its context — but it cannot contradict it without the LMF ADR being updated or superseded first.

**LMF ADRs do not link down to instances.** The parent relationship is declared at the instance level only. LMF ADRs remain universal and do not enumerate their adopters — that list would rot as instances come and go.

## Consequences

**Enables:**
- Auditable inheritance: given any instance ADR, you can trace its architectural lineage to LMF
- Propagation discipline: when an LMF ADR is updated or superseded, existing `parent_adr` references surface which instance ADRs need review
- Onboarding clarity: a new instance can grep for `parent_adr: lmf-adr-NNN` to find all prior implementations of an LMF decision

**Forecloses:**
- Implicit-only inheritance — if an instance ADR implements an LMF decision, it must declare it

**Trade-offs:**
- Existing ADRs (Prosper0-ADR-001 through 007, Ariel-ADR-001) need backfill where applicable — low effort but requires a pass
- No automated enforcement; the field is a convention, not a constraint
