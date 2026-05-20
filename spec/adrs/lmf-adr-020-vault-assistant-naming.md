---
title: "LMF-ADR-020: Vault Assistant as Canonical Assistant Class Name"
type: adr
project: Local Mind Framework
status: accepted
date: 2026-05-11
tags: [adr, lmf, naming, vault-assistant, ariel]
---

## Context

LMF instances each have an AI assistant persona. The persona was originally designed around "Ariel" — Jared's instance name — making the class name and instance name conflated. As LMF grows to support multiple operators (Scribner, Jason's instance, family deployments), the framework needs a clean separation between:

- The *class* of assistant LMF defines (framework level, model-agnostic, reusable)
- The *name* the operator gives their assistant (instance level, personal, vault-specific)

The existing convention `<Name> von <Vault>` already encodes the instance suffix, but the class had no canonical name. "Ariel" was doing double duty.

## Decision

The LMF canonical class name for the assistant is **Vault Assistant**.

Instance naming convention: `<Operator-chosen name> von <Vault name>`

Examples:
- Jared's instance: **Ariel von Marlin**
- Jared's brother's instance: **Jocasta Nu von [VaultName]**
- Scribner instance: **[Name TBD] von Scribner**

The LMF codebase (currently at `~/git/ariel/`) will be reorganized under LMF as the `vault_assistant` module. "Ariel" is not a framework concept — she is Jared's operator-named assistant running on the framework.

## Consequences

- `~/git/ariel/` migrates into the LMF repository as `vault_assistant/` (or similar module path) — see migration task
- ADR-014 (Persona over Model) remains in force: the operator names the assistant, not the vendor or model
- Scribner's AI persona field (`[Name TBD] von Scribner`) can now be filled without waiting for framework clarity
- Documentation, READMEs, and CLAUDE.md files that reference "Ariel" as a framework concept should be updated to reference "Vault Assistant" at the class level and "Ariel" at the instance level
- lmf-adr-001 references the old name "Local Mind Foundation" — superseded by the rename to "Local Mind Framework" (see rename task)

