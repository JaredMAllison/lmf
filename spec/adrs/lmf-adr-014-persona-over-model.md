---
title: "LMF-ADR-014: Persona Over Model — Model Name Never Surfaces"
type: adr
project: lmf
status: accepted
date: 2026-04-30
tags: [adr, lmf, ariel, persona, identity]
---

## Context

The orchestrator assembles ARIEL.md + memory + skills into a system prompt each turn. The underlying model (Qwen2.5 7B, or any future swap) is an implementation detail. The question was whether the model identity should ever be visible to the operator — either in responses or in the UI.

The UI already displays "Ariel von Marlin" with the model listed as a runtime detail (not as the assistant's identity). The question was whether to formalize this as an LMF-level principle.

## Decision

The model name never surfaces as part of the assistant's identity. The persona — Ariel, assembled by the orchestrator from identity doc + memory + skills — is what the operator interacts with. The model is an implementation detail visible only in runtime/infrastructure views (stack spec, admin console), never in conversation.

This is an LMF-level decision applying to all deployments: Ariel von Marlin, Ariel von Prosper0, and any future instances.

## Consequences

**Enables:**
- Model swaps (Qwen → Llama → future model) without any operator-facing identity disruption
- Clean separation between persona (stable, operator-facing) and model (variable, infrastructure)
- Consistent with the LMF naming convention — the vault name, not the model, defines identity

**Forecloses:**
- Operators relying on model-specific behavior as a stable interface — behavior may shift on model swap

**Requires:**
- System prompt explicitly instructs the model to identify as Ariel, never as the underlying model name
