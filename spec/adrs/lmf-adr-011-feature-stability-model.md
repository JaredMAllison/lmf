---
title: "LMF-ADR-011: Feature Stability Model"
type: adr
project: Local Mind Foundation
status: accepted
date: 2026-04-21
tags: [adr, lmf, stability, quality, testing]
---

## Context

LMF features are built by one author against one neurological profile. There is no formal mechanism to distinguish "works for Jared" from "works for ND people broadly" from "untested claim." This matters as LMF moves toward external validation and eventually community use.

The risk: features ship as if they're universal when they've only been validated for a single operator. This undermines the architecture's credibility and creates friction for new users whose profiles differ from the author's.

## Decision

Adopt a three-tier feature stability model with a parallel community trust dimension.

### Stability Tiers (code/profile maturity)

| Tier | Name | Definition |
|---|---|---|
| 0 | **Experimental** | Built and used by author. No external validation. |
| 1 | **Tested** | Used by at least one non-author operator on a discrete problem without modification. |
| 2 | **Stable** | Tested across multiple neurological profiles without requiring modification to work. |

**Stability is profile-specific, not universal.** A feature may be Stable for ADHD + working-memory deficits and Experimental for autism-without-ADHD. Each feature carries context tags: which profiles it's been tested against, which profiles it's known to work for, which remain untested.

### Community Trust Tiers (adoption weight)

A feature's community trust tier is determined by real-world deployment and review data:

| Tier | Name | Criteria | Label |
|---|---|---|---|
| -1 | **Abandoned** | Built for a reason; operator moved away (stated or unknown) | Legacy/Abandoned |
| 0 | **Solo** | Author only | Author-only |
| 1 | **Vouched** | ≥2 operators, ≥1 contributed review | Peer-backed |
| 2 | **Validated** | ≥3 operators, ≥2 contributor reviews | Community-validated |

A feature or panel's full maturity is expressed as a pair: `Stability/Trust`. For example:
- `Tested/Vouched` — confirmed to work by one non-author who also reviewed it
- `Stable/Validated` — proven across profiles with community confirmation
- `Experimental/Solo` — default for all new contributions

Community trust advances when an operator reports: "I deployed this, it worked for my profile, here are any notes." The feature's record in `features/panels/registry.json` tracks these reports.

### Combined Matrix

| | Solo | Vouched | Validated |
|---|---|---|---|
| **Experimental** | New panels, personal tools | Two people using it, one reviewed | — |
| **Tested** | Non-author ran it, no review yet | Tested + peer-backed | Tested across profiles with community confirmation |
| **Stable** | — | Broadly works, one review | Gold standard |

**Scope:** The model applies to interaction patterns, skill behaviors, vault conventions, and cockpit panels — not just code. Git tracks code; this model covers the behavioral and adoption layer.

**Evidence base:** The per-profile stability record and per-feature trust count are the systematic answer to "does this architecture transfer?" — replacing assertion with documented observation.

## Consequences

**Enables:**
- Honest communication with external users about what has and hasn't been validated
- A research posture: each new user is a test case that advances the stability and trust tiers of the features they use
- Credible claims: "vouched by two operators, validated across three profiles" is defensible; "works for everyone" is not
- Prioritization: Experimental/Solo features don't get distribution infrastructure until they clear Tested or Vouched
- Library browsing: users can filter by trust tier — "show me only vouched panels"

**Forecloses:**
- Treating the author's daily use as sufficient validation for community recommendation
- Silent universality assumptions in feature documentation
- A single-author panel appearing alongside community-validated ones without differentiation

**Trade-offs:**
- Most current features are Experimental/Solo. This is honest but means the table starts nearly empty.
- Tracking trust requires operators to submit "I used this" reports — lightweight but needs a mechanism (a webhook, a label in the repo, a vault skill)
- The trust model is cumulative: once a feature reaches Validated, it stays there unless a critical bug emerges
