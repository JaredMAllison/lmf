---
title: "LMF-ADR-006: Instance Trust Profiles"
type: adr
project: Local Mind Foundation
status: accepted
date: 2026-04-20
tags: [adr, lmf, architecture, enforcement, trust, instances]
---

## Context

The Prosper0 enforcement layer was built to satisfy a specific threat model: an employer who needs cryptographic guarantees that the AI cannot self-escalate its privileges, exfiltrate data without a paper trail, or operate without an audit record. That mechanism — Ed25519-signed config, AuditLogger, TransferGate, fail-closed chain — is correct for that context.

But LMF is a general architecture. Applying the full Prosper0 enforcement model to every instance is wrong. A personal secretary running on the operator's own hardware has no employer, no third-party trust relationship, and no threat model that justifies a cryptographic audit trail. Adding it there creates friction without benefit.

At the same time, other instance types do need enforcement — just for different reasons and different third parties. A safer AI instance needs a parent's oversight. A household brain may need shared-operator coordination. These are structurally similar to the work brain model but serve different purposes.

LMF needs a named set of instance trust profiles so that enforcement decisions are made at the profile level, not re-decided per instance.

## Decision

Define four LMF instance trust profiles. Each profile specifies what enforcement components are required, optional, or excluded.

---

### Profile 1: Personal Secretary

**Example instance:** Ariel von Marlin

**Relationship:** Operator only. No third-party trust.

**Enforcement:**
- `tools.config.yaml` path scoping — required (basic safety, prevents path traversal)
- Ed25519 signing — not applicable (no third party to hold the key)
- AuditLogger — not required
- TransferGate — not required
- Fail-closed chain — not required; tools.config.yaml validation still fails closed at startup

**Philosophy:** The operator trusts themselves. Path scoping prevents accidents. Everything else is overhead.

---

### Profile 2: Work Brain

**Example instance:** Prosper0

**Relationship:** Operator + employer. Employer is a third party with a legitimate interest in AI activity on their data.

**Enforcement:**
- `tools.config.yaml` path scoping — required
- Ed25519 signing — required (employer holds the private key; operator cannot self-escalate)
- AuditLogger — required (every tool call logged with timestamp, input summary, outcome)
- TransferGate — required (operator self-certifies transfers; employer receives full content + hash)
- Fail-closed chain — required (enforcement stops rather than degrades)

**Philosophy:** The employer cannot be present at every session. Enforcement must be structural and independently verifiable — not dependent on the operator's good faith.

---

### Profile 3: Safer AI for Young Operators

**Example instance:** A school-age person already using ChatGPT, Character.AI, etc.

**Relationship:** Young operator + parent/guardian. Parent holds the key. This profile exists because young people are already using AI — the choice is between unmonitored commercial AI and a locally sovereign environment designed for their safety.

**Positioning:** This is not a "safer AI tool." It is a harm-reduction response to the reality that kids are already interacting with AI systems that have no guardrails, no parental visibility, and extractive incentives. LMF provides an alternative that:
- Runs locally — no data leaves the machine
- Gives parents visibility without surveillance (audit log, not keystroke logging)
- Lets the young person explore, create, and ask questions in a private space
- Grows with them — the enforcement profile graduates as they get older

**Enforcement:**
- `tools.config.yaml` path scoping — required
- Ed25519 signing — required (parent holds the private key; young operator cannot self-escalate privileges or expand content access)
- AuditLogger — required (activity log visible to parent on demand, not continuously — parent can check when they need to)
- TransferGate — required (data leaving the instance requires parent visibility)
- Fail-closed chain — required
- Content policy fields — required (topic allowlists/denylists, age-appropriate access controls; extends `tools.config.yaml` schema beyond what Work Brain needs)

**Philosophy:** Same cryptographic trust model as Work Brain — a third party holds the key, the young operator cannot modify their own constraints. The difference is purpose: not preventing data exfiltration for an employer, but creating a safe exploratory space for a young person who would otherwise use commercial AI with no protections.

**Divergence from Work Brain:**
- The audit trail serves the parent's protective interest, not an employer's data sovereignty interest
- `tools.config.yaml` gains content policy fields not present in Work Brain
- Time-of-day and session duration limits are a natural extension (out of scope for this ADR)
- The model is graduation — as the young person demonstrates readiness, enforcement softens. The profile is temporary, not permanent.

---

### Profile 4: Household Brain

**Example instance:** A shared household exobrain (e.g., future Ivy instance)

**Relationship:** Multiple adult operators. No external third party.

**Enforcement:**
- `tools.config.yaml` path scoping — required
- Ed25519 signing — optional (may be useful if one operator administers the config for others, but not required)
- AuditLogger — optional (shared context may benefit from an activity log, but no external accountability requirement)
- TransferGate — not required
- Fail-closed chain — recommended if AuditLogger is active

**Philosophy:** Shared-operator trust is peer trust — no one party holds authority over the others. Enforcement exists for coordination and accident prevention, not third-party accountability. Profile is deliberately underspecified pending a real household brain implementation.

---

### Profile 5: Close Family

See [[lmf-adr-019-close-family-trust-profile]] for full detail.

**Example instances:** Jason (brother, sibling pilot), Tori (partner, writing collaborator)

**Relationship:** Two-person sponsor relationship. Jared is the deployer and seed author. The family member is the operator. No external third party.

**Enforcement:**
- `tools.config.yaml` path scoping — required (base safety)
- Ed25519 signing — not required (consenting adult, self-managing)
- AuditLogger — not required
- TransferGate — not required
- Fail-closed chain — not required
- Content policy fields — not required

**Init variant:** Seeded — Jared pre-populates a profile seed with confidence tags (high/medium/low), the family member confirms or corrects before the system commits.

**Philosophy:** Jared knows this person well. Trust is established outside the system. The seed is a gift of context, not a constraint. The operator corrects what doesn't fit and owns the result.

---

### Enforcement Component Matrix

| Component | Personal | Work | Safer AI (Young) | Household | Close Family |
|---|---|---|---|---|---|---|
| tools.config.yaml scoping | ✓ required | ✓ required | ✓ required | ✓ required | ✓ required |
| Ed25519 signing | — | ✓ required | ✓ required | ○ optional | — |
| AuditLogger | — | ✓ required | ✓ required | ○ optional | — |
| TransferGate | — | ✓ required | ✓ required | — | — |
| Fail-closed chain | — | ✓ required | ✓ required | ○ if audit active | — |
| Content policy fields | — | — | ✓ required | — | — |

---

### Profile Declaration

Each instance declares its profile in `tools.config.yaml`:

```yaml
version: 1
profile: personal   # personal | work | child | household
signed_by: ""       # required for work and child profiles
```

The orchestrator reads `profile` at startup and validates that the active enforcement components match the profile requirements. A work-profile instance missing a signature fails closed. A personal-profile instance does not load the enforcement chain.

## Consequences

**Enables:**
- Correct enforcement per context — no over-enforcement on personal instances, no under-enforcement on work or child instances
- A clear architectural basis for new instance types — add a profile, define its matrix, done
- Child brain as a first-class LMF instance type, not an afterthought
- Household brain scoped loosely now, tightened when a real instance is built

**Forecloses:**
- Ad-hoc enforcement decisions per instance — enforcement is now profile-driven, not instance-driven
- Shipping the full Prosper0 enforcement stack as the default — Personal Secretary is the lighter default for most users

**Trade-offs:**
- Household Brain is underspecified — this is intentional. Specifying it before building it would produce wrong decisions. Revisit when Ivy or an equivalent is scoped.
- Content policy fields for Child Brain extend the `tools.config.yaml` schema in ways not yet designed — that is a Child Brain ADR, not this one.
