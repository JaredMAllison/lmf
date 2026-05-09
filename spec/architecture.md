# LMF Architecture

A self-building cognitive operating system for ND people, structured around a living profile document that the assistant draws context from, onboards through conversation, and maintains through scheduled and feature-driven review.

## Core Concept

The operator talks; the system listens, learns, and builds structure around what they say. The assistant is the collaborator — not the tool. The operator owns the brain; the system maintains it.

## Profile Document

`LOCAL_MIND_FOUNDATION.md` lives at the vault root. It has:
- Machine-readable frontmatter (the cognitive profile)
- A body with declaration, architecture, and active features
- Git history tracking its evolution over time

## Three Script Types

| Script | Trigger | Purpose |
|---|---|---|
| init | Profile fields empty | Conversational onboarding |
| cron | Calendar interval | Periodic review |
| feature | New capability lands | Feature discovery |

## Instance Trust Profiles

Five profiles govern enforcement per instance. See `spec/adrs/` for full detail.

## Design Principles

See `spec/principles.md` and the ADR series in `spec/adrs/`.
