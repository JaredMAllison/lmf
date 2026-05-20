---
title: "LMF-ADR-007: Model-Agnostic Skill Format"
type: adr
project: Local Mind Foundation
status: accepted
date: 2026-04-20
tags: [adr, lmf, skills, orchestrator, architecture]
parent_adr: lmf-adr-001-local-mind-foundation-architecture
---

## Context

Claude skills are written with Claude Code tool names inline: `Read`, `Write`, `Edit`, `Glob`, `Grep`. These are implementation details of one specific model interface. When Ariel von Marlin (Qwen2.5 7B via Ollama) needs to execute the same skill, those tool names are meaningless — her tools are `read_file`, `write_file`, `list_directory`.

The naive fix is to maintain separate skill files per model. That creates duplication: the logic, steps, vault paths, and operator-facing language are identical. Only the tool references differ. Duplicate files diverge over time.

The deeper problem: skills are instructions, not tool bindings. A skill that says "read Inbox.md and append a timestamped line" is model-agnostic. A skill that says "use `Read` to open Inbox.md" is Claude-specific. The latter is an accidental constraint.

## Decision

Skills are written in plain imperative language. Tool names are never referenced in skill bodies. The orchestrator is responsible for translating intent into the correct tool calls for the active model.

**Skill format:**

```markdown
---
name: skill-name
description: "Trigger phrases and capability summary."
tools_required: [read, write, list]   # abstract capability names, not model tool names
---

# Skill Name

Instructions written as plain imperatives:
- "Read the file at /vault/Inbox.md"
- "Append a timestamped line to Inbox.md"
- "List the contents of /vault/Tasks/"

Never: "Use `Read` to open...", "Call `write_file` with...", "Run `Glob` against..."
```

**Abstract tool vocabulary:**

| Abstract name | Claude tool | Ariel tool |
|---|---|---|
| `read` | `Read` | `read_file` |
| `write` | `Write` | `write_file` |
| `edit` | `Edit` | `write_file` (full rewrite) |
| `list` | `Glob` | `list_directory` |
| `search` | `Grep` | ❌ not yet available |
| `bash` | `Bash` | ❌ not applicable |

**`tools_required` frontmatter field** declares which abstract capabilities the skill needs. The orchestrator uses this to:
1. Verify the active model has the required tools before injecting the skill
2. Skip skills the model cannot execute rather than injecting broken instructions

**Existing Claude skills** are exempt from immediate rewrite — they work as-is for Claude. New skills and any skill that needs to run on Ariel should follow the model-agnostic format. Migration is opportunistic.

## Consequences

**Enables:**
- One skill file serves all LMF model instances — no duplication
- Skills are portable across model upgrades and swaps
- The orchestrator can validate skill compatibility before injection
- Skills authored today work for future models without modification

**Forecloses:**
- Model-specific optimization in skill bodies (a skill can't say "use chain-of-thought" for Claude and a different strategy for a smaller model) — that belongs in the orchestrator, not the skill

**Trade-offs:**
- Existing Claude skills need migration to become truly portable — this is opportunistic, not a blocking rewrite
- `search` (Grep equivalent) doesn't exist in Ariel's toolbelt yet — skills requiring it cannot run on Ariel until the tool is built
- "Plain imperative language" requires discipline — it's easy to slip back into tool-name references
