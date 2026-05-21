---
title: "LMF-ADR-024: Knowledge Loom as canonical grounding infrastructure service"
type: adr
status: accepted
date: 2026-05-20
tags: [adr, lmf, grounding, services, infrastructure, knowledge-loom]
---

## Context

LMF's AI layer (Ariel and equivalents) requires a grounding layer — a mechanism to search, read, and navigate operator vault content in real time. Without grounding, the AI operates only from what fits in context, which breaks object permanence for notes and makes the system unreliable for vault-aware tasks.

The LMF spec described this grounding layer as required infrastructure but left the implementation unspecified. Two candidate approaches existed:

1. Build a vault search tool inside the LMF stack
2. Adopt an external tool built by a collaborator with the right architecture

Knowledge Loom (`odinkirk/knowledge-loom`) is a Rust binary that indexes Markdown vaults and exposes BM25, semantic vector, and wikilink graph search via MCP tools (`loom_*`). It was built by Fritz (GitHub: odinkirk), an infrastructure collaborator who has been actively building and maintaining the tool — including a Marlin-specific homestack integration — and who reached production viability in May 2026 with the MCP smoke test fixes (PR #11).

## Decision

Adopt Knowledge Loom as the canonical grounding infrastructure service for LMF. It is:

- **Required** for vault-aware LMF instances (not optional)
- **Externally maintained** by Fritz (odinkirk) — LMF does not fork it
- **Modeled as a `service` type** in the LMF feature schema, establishing the first entry in `features/services/`
- **Credited by maintainer** in the service spec — Fritz is listed as `upstream-maintainer`, a distinct role from panel or skill contributors who submit into the LMF repo itself

The `features/services/` directory and `catalog.json` are created to model service-type dependencies: background processes and tools that LMF instances depend on but do not contain.

The upstream-not-fork principle (LMF-ADR-004) applies: LMF references Knowledge Loom's upstream repo, does not maintain a copy, and instance operators are responsible for keeping the binary current.

## Consequences

**Enables:**
- Ariel and equivalent AI layers can search, read, and edit the vault via `loom_*` MCP tools
- Skills can be vault-aware: query project state, find related notes, read section content without requiring manual paste
- The Feature Manager can eventually use vault content to inform feature surfacing
- A formal model exists for external collaborator tools that LMF depends on

**Forecloses:**
- LMF cannot make breaking changes to the loom API — it must track the upstream
- Instances that cannot run a Rust binary (constrained environments) cannot use vault-aware features

**Trade-offs:**
- Fritz maintains the tool; LMF has no direct control over the release cadence or API stability
- This is acceptable because Fritz is a known collaborator with active investment in the Marlin use case

**Establishes:**
- The `service` type as a first-class LMF feature category alongside `panel`, `skill`, `plugin`
- The `maintainer.role: upstream-maintainer` attribution pattern for externally-owned services

## Compliance

- `features/services/catalog.json` — service discovery entry
- `features/services/specs/knowledge-loom.json` — full service spec with maintainer attribution
- Instance `.mcp.json` must declare the `knowledge-loom` server
- Instance `.gitignore` must exclude `.knowledge-loom/` and `.knowledge-loom-index/`
