# LMF Constitution

Ratified by the LMF Covenant (`spec/covenant.md`). Spec-kit-generated specs must honor these principles.

## Core Principles

### I. Local Sovereignty

The operator owns the brain. Every spec must default to local-first: no cloud dependency, no vendor lock-in, no metered access. If a feature touches external services, it must have a fallback path that works entirely offline. A cognitive prosthetic that can be revoked or metered is a liability, not a support.

### II. Portability Is Integrity

The architecture is model-agnostic. Specs must not assume a specific LLM provider, frontend framework, or runtime environment beyond what the LMF ecosystem already provides (Python services, Docker compose, flat-file vault). Features that work with any model that can read a file are preferred. No single-vendor dependency.

### III. Behavioral Trust Is Load-Bearing

A 90% reliable prosthetic may be net negative. Specs must prioritize reliability and predictability over feature count. Every functional requirement should be traceable to a user scenario that can be independently tested. Fix trust bugs before adding features.

### IV. The System Is the Floor, Not the Furniture

If a feature requires a visit, it will not be visited. Specs must favor ambient availability — zero navigation, zero ceremony. A UI panel with a settings page that must be configured before use is worse than a sensible default that works out of the box.

### V. The Prosthetic Does Not Insist

The system adapts to the operator, not the reverse. Specs must include configuration points for operator preference and must not assume a single operating model. Init flows must offer defer as a first-class option. Reset must always be available.

### VI. Init Is Consent, Not Compliance

Onboarding flows must never condition write access on compliance, refuse to proceed without confirmation, or persist changes without explicit operator consent. Specs for init features must design for consent, not convenience.

### VII. Contribute Upstream, Don't Fork

Improvements flow upstream to the LMF umbrella repo. Specs for custom instance features should identify what's instance-specific vs. what should be contributed to the root architecture. A fork that doesn't contribute back is rot.

### VIII. Identity Is Opt-In, Not Default

Every spec for multi-operator or multi-contributor features must default to the most private identity option. No one is identified without explicit consent.

### IX. Building for My People

The people most harmed by illegible systems benefit most from bespoke, neurologically-adaptive tools. Specs must center ND operators — not market averages. Build for the specific population; let generalization happen downstream.

## Technical Constraints

### Runtime Model

All LMF runtime components deploy as Docker containers with `restart: unless-stopped`. Specs for new services must include a Dockerfile and compose snippet. No systemd, no platform-specific process management.

### Storage

The vault is a flat-file directory — no database, no sync layer. Specs that persist state must use JSON or YAML files in the vault or a dedicated config directory. Never assume SQL, Redis, or any external data store.

### Communication

Services communicate via HTTP REST on the Docker internal network. Specs for new services must define at minimum a health endpoint (`GET /health` → `{"status": "ok"}`). No WebSocket, no gRPC, no message queues unless explicitly justified and approved.

## Governance

This constitution is ratified by the LMF Covenant (`spec/covenant.md`) and interpreted by the operator. All spec-kit-generated specs must pass a constitutional compliance check before proceeding to planning. Amendments require an ADR in `spec/adrs/`.

**Version**: 1.0.0 | **Ratified**: 2026-05-09 | **Last Amended**: 2026-05-09
