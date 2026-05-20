---
title: "LMF-ADR-004: Contribution Model — Upstream Not Fork"
type: adr
project: Local Mind Foundation
status: accepted
date: 2026-04-19
tags: [adr, lmf]
---

## Context

As LMF grows toward community use, operators will naturally develop accommodations, patterns, and tools suited to their specific cognitive profiles. The question is whether those contributions live in forks or flow back to the root architecture.

## Decision

Operators are encouraged to contribute accommodations back to the root rather than maintain private forks. Contributions include self-identified cognitive profile tags (e.g. working-memory, ADHD, sensory-sensitivity, task-avoidance, executive-function). Contributors may anonymize if desired.

This creates a searchable compatibility matrix: operators can find tools tested against profiles matching their own, and the assistant can provide more accurate tool matches based on declared profile.

## Consequences

**Enables:**
- A living, community-curated knowledge base of what works for which cognitive profiles
- More accurate onboarding — the assistant can cross-reference incoming profile against existing matches
- Stability labels become meaningful: "tested for ADHD, untested for autism-without-ADHD" is a real signal
- The architecture improves for everyone, not just for whoever forked it

**Forecloses:**
- Forks that diverge silently — operators who fork instead of contributing create asynchronous tools, data, and solutions that can't benefit anyone else

**Trade-offs:**
- Requires a contribution interface and governance model (lightweight — PRs or Discussions, not a formal committee)
- Anonymization must be structurally guaranteed, not just policy-promised
