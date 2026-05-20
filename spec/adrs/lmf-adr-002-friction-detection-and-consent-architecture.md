---
title: "LMF-ADR-002: Friction Detection as Systemic Property and Consent Architecture"
type: adr
project: Local Mind Foundation
status: accepted
date: 2026-04-17
tags: [adr, lmf, friction, consent, architecture]
---

## Context

The operator's drive to find and engineer away friction is a cognitive trait — common in syseng-type minds, but not universal. LMF cannot depend on any user having it. Users may not perceive their own friction (low-insight), may perceive it but lack executive capacity to act (low-bandwidth), or may want to be the friction engineer themselves (syseng-type who resents the system acting without them).

The system must hold the complete friction-repair loop regardless of user predilection. Detection, diagnosis, and repair initiation cannot be outsourced to the operator.

## Decision

**Friction detection is a systemic property of LMF, not a user-dependent behavior.**

Three user states require different repair postures:

| User state | System posture |
|---|---|
| Cannot see friction | Surface it |
| Sees it, can't/won't act | Surface → propose → handle with consent |
| Syseng type (wants agency) | Surface → diagnose → hand off |

**Two-axis adaptation model:**
- **Cognitive style profile** — set at onboarding or inferred over time; determines *default* repair posture
- **Bandwidth signal** — real-time; overrides style when capacity is low. As bandwidth drops, the system acts more and involves less, regardless of style preference.

**Consent architecture — four steps, always:**

1. **Surface** — here's something
2. **Propose** — here's what I'd do
3. **Consent** — yes / no / show me why
4. **Execute** — only after yes

The "show me why" press exposes backend logic — the reasoning behind the proposal. This serves both the low-engagement user (one tap to accept) and the skeptical systems-thinker (full inspection before accepting, modifying, or rejecting).

**The system's self-framing:** *"This is your brain. I'm good at organizing and collaborating."* The system has no agenda and no preference for its own suggestions. The operator is the consent layer, not the labor layer.

## Consequences

**Enables:**
- LMF serves users who cannot see or act on their own friction — not just users who already have the drive to fix it
- Syseng-type users retain full agency without the system acting opaquely
- The consent model is always legible — users can always understand why
- Bandwidth adaptation is automatic; no user configuration required
- Style inference can be wrong without catastrophic consequences — consent catches errors

**Forecloses:**
- Silent autonomous action: the system never executes structural changes without consent
- Friction repair as a user responsibility: the architecture owns detection and proposal

**Open questions:**
- The consent loop adds latency. For high-volume friction events it may need batching or prioritization — not resolved here.
- Style profile must be inferred or declared at onboarding; wrong inference produces friction of its own. Correction pathway TBD.
- What signals constitute "bandwidth"? Real-time measurement approach is unspecified.
