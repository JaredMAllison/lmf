---
title: "LMF-ADR-013: Skill Index Auto-Generated from Frontmatter"
type: adr
project: lmf
status: accepted
date: 2026-04-30
tags: [adr, lmf, ariel, skills, orchestrator]
---

## Context

The orchestrator needs to know which skills are available and when to surface them. Two approaches:
- **Hand-maintained index** — a separate file listing skills and their triggers
- **Auto-generated index** — orchestrator reads skill file frontmatter at startup and builds the index dynamically

## Decision

Skill index is auto-generated at orchestrator startup from skill file frontmatter. Each skill file declares `name`, `description`, and trigger phrases in its frontmatter. The orchestrator reads the skills directory, parses frontmatter, and builds a match index. Incoming messages are matched against this index to determine which skills to inject.

## Consequences

**Enables:**
- Adding a skill is a single operation — write the file with correct frontmatter, done
- No sync problem between the skill files and a separate index
- Consistent with LMF-ADR-007 (model-agnostic skill format using plain imperatives + frontmatter)

**Forecloses:**
- Manual curation of skill ordering or priority outside the frontmatter itself

**Requires:**
- Consistent frontmatter discipline on every skill file — vague descriptions produce poor matching
- Skill authoring standard: `description` must include concrete trigger phrases, not just capability summaries
