---
title: "LMF-ADR-001: Contribution Architecture and Instance Evidence Model"
type: adr
project: local-mind-foundation
status: accepted
date: 2026-05-03
tags: [adr, lmf, contribution-architecture, instance-model]
---

## Context

The Local Mind Foundation framework needs a contribution model that:

1. Allows anyone to add new prosthetics, tools, chrome, and configurations
2. Provides empirical evidence of what works, for which profiles, at what scale
3. Protects operator privacy — contributors and instance operators may be in vulnerable populations
4. Does not impose bureaucratic gates on low-risk contributions (sounds, themes)
5. Does maintain meaningful review for high-risk contributions (write tools, core architecture)

The naive models were too heavy ("all contributions require full review") or too light ("any contribution can claim multi-instance status unilaterally").

## Decision

### Stack Naming Convention

LMF instances are identified by stack type: `lmf-[storage]-[llm]`

- `storage` — the vault/data layer (e.g., `obsidian`, `sqlite`)
- `llm` — the inference stack (e.g., `ollama`, `claude`, `openai`)

The current reference implementation is `lmf-ollama-obsidian`. This naming captures compatibility — two instances of the same stack type can share contributions directly.

### Variable Dimensions of an Instance

Every LMF instance is defined across these variable dimensions:

| Dimension | Examples |
|---|---|
| Hardware | GPU/CPU, RAM, device name |
| LLM stack | Ollama local, Ollama remote, cloud API |
| Model | qwen2.5:7b, llama3.2, claude-sonnet |
| Storage | Obsidian flat-file, SQLite |
| File structure | Vault root path, directory conventions |
| Services | marlin.py, webhook.py, TTF, Cockpit |
| Tools | Write-gate, MCP servers, available actions |
| Operator declarations | The operator profile (JARED.md equivalent) |
| Network | WireGuard, LAN topology, external access |
| Sync | Syncthing nodes, vault sync paths |
| UI/chrome | Sounds, Cockpit theme, assistant name |
| Naming | Vault name, assistant name |

Stack type names capture storage + LLM only — the two dimensions that define inter-instance compatibility. Everything else is instance configuration.

### Contribution Status Model

A contribution's status reflects empirical evidence, not endorsement:

| Status | Condition |
|---|---|
| `unproven` | Active in one instance. Personal validation only. |
| `multi-instance` | Active in 2+ instances. Evidence threshold met (see review tiers below). |
| `proven` | Active in 3+ instances across 2+ profiles. Strongest evidence. |

The counter shows anonymous evidence: `instances: ▓▓▓░░ (3 active)`. Instance identities are hashed by default. Identity disclosure is operator opt-in.

### Review Tiers by Contribution Type

Review requirements are calibrated to risk, not applied uniformly:

| Contribution Type | Examples | Review Required for Multi-Instance? |
|---|---|---|
| Chrome / aesthetic | Sounds, Cockpit themes, color palettes | No — evidence only |
| Configuration | Port conventions, vault path patterns | No — no code |
| Prompts / onboarding | Vault skeleton, conversation scripts | Lightweight peer review |
| Write-capable tools | MCP tools with write access, backend routes | Yes — code + privacy review |
| Core architecture | build_prompt.py, orchestrator.py, data model | Yes — full code review |

Low-risk contributions advance on evidence alone. High-risk contributions require peer review before multi-instance status — not because the framework distrusts contributors, but because write capabilities and core architecture have blast radius across every operator's data.

### Privacy Architecture

- Instance names are stored as hashed identifiers in public records
- No personal data is collected by the framework itself
- Identity disclosure requires explicit operator opt-in
- The counter shows the pattern, not the person

## Consequences

**Enables:**
- Jason contributing sounds immediately, with no process friction
- Community growth without a bureaucratic bottleneck on aesthetic contributions
- Meaningful evidence that specific prosthetics work at scale
- A clear pathway from personal validation → community validation → proven evidence
- Privacy protection for operators who may not want their neurological profiles public

**Forecloses:**
- Unilateral "multi-instance" claims for write tools without peer review
- Anonymous high-risk contributions that bypass safety checks

**Trade-offs:**
- "Proven" status still requires Jared's involvement as the current single reviewer — this becomes a bottleneck as the framework grows. Future: any `proven` contributor can review.
- Hashed identity makes the evidence less legible (can't see who is using what) — this is intentional and acceptable.
