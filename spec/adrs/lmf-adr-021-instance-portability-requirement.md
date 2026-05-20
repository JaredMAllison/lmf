---
title: "LMF-ADR-021: Instance Portability Requirement"
type: adr
project: Local Mind Framework
status: accepted
date: 2026-05-12
tags: [adr, lmf, resilience, portability, deployment]
---

## Context

A cognitive prosthetic that dies with its hardware is not a prosthetic — it is a liability. LMF instances are designed for neurodivergent operators who depend on their second brain for executive function, task management, and daily orientation. If the host machine fails, the operator loses not just a tool but a compensatory cognitive layer at exactly the moment they can least afford to rebuild it.

Early LMF deployments (Marlin on Gretchen, Jason's USB instance) exposed a structural gap: the vault and services were tied to a single hardware node with no documented recovery path. ADR-017 addressed encryption of the vault on USB for work instances, but did not establish a general resilience requirement across all deployments.

The principle that emerged: **the vault must outlive the hardware**.

## Decision

Every LMF instance deployment is incomplete until it includes a portable recovery artifact — a self-contained bundle from which the instance can be fully restored on any compatible host without network access to the original machine.

A conforming recovery artifact must contain:

1. **Vault snapshot** — a complete copy of the instance vault at a known point in time
2. **Service code** — the orchestrator, surfacing engine, webhook handler, or equivalent for that instance's runtime
3. **Bootstrap script** — executable instructions to install dependencies, restore the vault, configure services, and bring the instance online
4. **Human-readable README** — a plain-language recovery guide legible to the operator under stress, without assumed context

The artifact must be:
- **Stored on physical media the operator controls** (USB drive, SD card, or equivalent offline storage)
- **Kept current** — refreshed after significant vault or code changes; a stale artifact is better than none, but a refresh cadence must be defined per instance
- **Tested** — the bootstrap path must be exercised at least once before the artifact is considered valid

This requirement applies to all LMF instances regardless of deployment model (local Linux, USB, cloud, mobile). The implementation varies; the requirement does not.

## Consequences

**Enables:**
- Any LMF instance can survive total hardware loss without data loss or extended downtime
- Operators can migrate between machines (planned or emergency) with a known, rehearsed procedure
- The recovery path is documented and legible under stress — when executive function is degraded, the README is the prosthetic for the prosthetic
- Deployment checklists for all instances (Scribner, future deployments) must include a life raft step before the deployment is marked complete

**Forecloses:**
- Treating a running instance as "done" without a recovery artifact — a running instance with no life raft is a deployment in progress, not a complete deployment

**Trade-offs:**
- Adds a maintenance obligation: the artifact must be refreshed. Instances should surface this as a recurring task so it doesn't silently go stale.
- Physical media can be lost. The portability requirement addresses hardware failure; physical media loss is a separate concern and may warrant a secondary copy strategy per operator preference.

**Relationship to ADR-017:** ADR-017 (encrypted vault USB) specifies that work instance vaults must be stored encrypted on USB as their *primary* store. This ADR is orthogonal — it governs the *recovery artifact* requirement across all instances, regardless of primary storage model.
