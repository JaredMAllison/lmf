# VAULT.md Specification

**Status:** Stub — fields named, design incomplete.

VAULT.md is the agnostic grounding file at the root of any LMF vault — home vault or extension. It defines what the vault is, the operator's frame preference, and the role archetype for dispatched models. Model-agnostic: any model that can read a file can parse a VAULT.md.

Vendor-specific adapter files (CLAUDE.md, opencode.md, AGENTS.md, API system prompts) are derived from this file, not written independently. The VAULT.md is the source of truth; adapters are delivery mechanisms.

---

## Named Fields

These are the required and optional fields every VAULT.md should define. The exact schema, validation rules, and adapter generation pipeline are downstream of a full design session.

### Required

| Field | Purpose |
|---|---|
| `vault_name` | Short identifier — home vault or extension name |
| `vault_type` | `home` or `extension`; determines init requirements |
| `operator_name` | The operator's handle or pseudonym |
| `frame_preference` | Which metaphor frame to use (e.g. `summons`, `office`, or `vocabulary`) |
| `role_archetype` | The behavioral contract for dispatched models — narrow job description |

### Optional

| Field | Purpose |
|---|---|
| `project_index` | Path to a project index file if this vault has one |
| `entry_point` | Suggested starting document for dispatched models |
| `grounding_context` | Additional context specific to this vault's purpose |
| `trust_profile` | One of the five LMF trust profiles, if different from instance default |

---

## Design Notes

- Vendor adapter derivation is not yet specified. The current CLAUDE.md and opencode.md are handwritten and may not fully match what VAULT.md would generate.
- The `VAULT.md` → `CLAUDE.md` adapter pipeline is a downstream deliverable — not yet designed, not yet built.
- This stub exists so the vocabulary has a referent. The implementation follows design.
