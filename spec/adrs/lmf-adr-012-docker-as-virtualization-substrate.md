---
title: "LMF-ADR-012: Docker as Adopted Virtualization Substrate"
type: adr
project: Local Mind Foundation
status: accepted
date: 2026-04-21
tags: [adr, lmf, architecture, docker, virtualization, deployment]
---

## Context

LMF-ADR-003 defined the virtualization layer with three abstract substrate options: `obsidian-flat-file`, `docker-volume`, and `conversation-only`. As Jared's instances move from design to active deployment — Prosper0 running its API server, Ariel running on Gretchen — a concrete technology decision is needed. "Docker volume" as an abstract option doesn't specify how instances are actually built, isolated, and run.

Without a committed substrate, each new instance risks re-deriving its deployment approach from scratch, and the "one architecture, many instances" goal remains theoretical.

## Decision

Docker Compose is the adopted virtualization substrate for all of Jared's LMF instances.

**What this means in practice:**

Each instance is a Compose stack. The stack topology per instance:
- `ollama` — local inference engine; GPU-accelerated via NVIDIA Container Toolkit where available
- `orchestrator` — system prompt builder + agent loop (Python)
- Supporting services as needed (webhook server, API layer, etc.)

**Vault isolation by substrate type:**
- `docker-volume` instances (Prosper0): vault lives in a named Docker volume; isolated from the host filesystem and from other instances by default
- `obsidian-flat-file` instances (Marlin): vault lives on the host filesystem, Syncthing-synced; Ariel runs in Docker but bind-mounts the vault directory

**GPU access:** NVIDIA Container Toolkit wires the host GPU into Docker containers. Ollama containers use `deploy.resources.reservations.devices` to claim the GPU. CPU fallback is automatic when GPU is unavailable (Gretchen CPU-only mode).

**Deployment targets all use the same pattern:**
- Gretchen (10.0.0.8) — primary runtime, `~/prosper0/deploy/docker-compose.yml`
- Desktop PC (RTX 3070, WSL2) — GPU inference target, same compose file with GPU reservation active
- 64GB USB (Prosper0 portable) — encrypted volume mounted as the vault; same compose pattern

Each instance repo contains `deploy/docker-compose.yml` as the source of truth for that instance's runtime.

## Consequences

- Prosper0 is fully containerized: vault as Docker volume, all services as containers
- Ariel von Marlin is a hybrid: vault on the filesystem (Syncthing), AI component (Ollama + orchestrator) in Docker
- USB deployment inherits this pattern: encrypted volume mount replaces the standard bind-mount or volume
- The `deploy/` directory is now a first-class project artifact — not an afterthought
- Docker Compose becomes the LMF-standard deployment format; any contributor building an instance has a clear template to follow
- This formalizes what was already implicitly true from Prosper0's `docker-compose.yml` and Gretchen's runtime

**Relation to ADR-003:** This ADR does not supersede ADR-003. The abstract substrate taxonomy remains valid for instances that don't use Docker (e.g., a future conversation-only packaged instance). This ADR records the specific substrate choice for Jared's instances.
