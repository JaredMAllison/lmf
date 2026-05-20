---
title: "LMF-ADR-023: RPG Vault Three-Field Lore Access Schema"
type: adr
project: lmf
status: accepted
date: 2026-05-20
tags: [adr, lmf, rpg, vault-schema, cockpit]
---

## Context

The LMF RPG Subscreen (panel.rpg) needs to filter lore notes by character knowledge and render them through a character's interpretive lens. This requires a schema that:

1. Controls which lore notes a character can access at all (access control)
2. Tracks what a specific character knows based on their arc position (position-based gating)
3. Records how a character interprets what they see (perspective/lens)

The naive solution — tagging every lore note with every character's name — doesn't scale and creates maintenance debt whenever a character's arc progresses. The problem is fundamentally about *authorization at a point in time*, not static tagging.

The schema also needs to generalize across TTRPG systems. Different systems use different vocabulary for knowledge tiers (mundane/occult/cosmic in CoC vs. common/enclave/touched/objective in the Unspoken World) but the underlying structure is identical.

---

## Decision

Three fields, three jobs, no overlap. Each field lives on a different note type.

### `revelation_tier` — on lore notes (access control)

```yaml
revelation_tier: [system-defined value]
```

Marks the canonical access level of a piece of lore. The vocabulary is system-defined and lives in the vault's schema declaration. The subscreen reads whatever tier vocabulary the vault declares.

This is the lock on the lore note. It does not change.

**Unspoken World vocabulary:** `common` · `enclave` · `touched` · `objective`

### `knowledge_tier` + `knows:` — on character notes (arc position + encounter history)

```yaml
knowledge_tier: [system-defined value]
knows:
  - [[Specific Lore Note]]
  - [[Another Lore Note]]
```

`knowledge_tier` is the general arc gate — a character at tier `enclave` can see everything tagged `common` and `enclave`. `knows:` is the specific encounter override — individual lore notes the character has encountered regardless of their general tier.

Together they handle two distinct ways a character gains knowledge: gradual arc progression (tier) and specific narrative events (knows).

This is the key the character carries. It advances as the arc progresses.

### `perspective:` — on character notes (interpretive lens)

```yaml
perspective: [system-defined value]
```

How the character interprets what they can see. Two characters at the same `knowledge_tier` may read the same lore through completely different frames. The perspective field marks which frame a note is written from, and which frame a character inhabits.

Drift from objective truth is not error — it is characterization. A character's perspective value is expected to shift across a campaign arc.

**Unspoken World vocabulary:** `objective` · `church` · `enclave` · `demon` · `character-name`

### Schema Declaration

The vocabulary lives in each vault's schema declaration: either a `CLAUDE.md` section or a dedicated `rpg-schema.yaml` in the vault root. The subscreen reads the declaration and adapts. No hardcoded tier names in the subscreen implementation.

---

## Consequences

**Enables:**
- Player mode: filter lore by `knowledge_tier` + `knows:`, render through `perspective:` lens
- GM gap view: character's filtered world alongside objective truth simultaneously — the killer feature; visible to the Teller without announcing it to the player
- Character switch: swap active character; filter reloads; same vault, different world
- System generalization: any TTRPG vault with Canon/ + Campaign/ + Engine/ structure and a schema declaration works; no schema changes needed in the subscreen itself

**Forecloses:**
- Arbitrary per-note character tagging (creates maintenance debt, doesn't generalize)
- Baking Unspoken World tier vocabulary into the subscreen (would break on any other system)

**Trade-offs:**
- Schema requires discipline: lore notes must have `revelation_tier`, character notes must have `knowledge_tier`, `knows:`, and `perspective:`. The subscreen cannot function on an unschema'd vault.
- `knows:` lists require manual maintenance as the campaign progresses. This is the Teller/player's job, not the subscreen's.

**Generalization table:**

| System | revelation_tier vocabulary | perspective vocabulary |
|---|---|---|
| Unspoken World | common / enclave / touched / objective | church / enclave / demon / character-name / objective |
| Call of Cthulhu | mundane / suspicious / occult / cosmic | sane / cracked / lost |
| D&D | tavern / regional / scholarly / secret | faction affiliations |
| Star Wars FFG | public / faction / force-sensitive / ancient | light / dark / neutral |

---

## Compliance

**Reference implementation:** `/home/jared/Documents/Obsidian/the-unspoken-codex/` — Sinners in Good Standing campaign vault, built to this spec 2026-05-20.

**Where to verify:**
- Lore notes in `Canon/` carry `revelation_tier:` — check any Canon note
- Character notes in `Campaign/Story-Teller/` carry `knowledge_tier:`, `perspective:`, `knows:` — see `Story-Teller.md`
- Schema vocabulary declared in `the-unspoken-codex/CLAUDE.md` under the Frontmatter Schema section
- Panel registration: `features/panels/registry.json` entry `panel.rpg` (port 8090, status: Planned)
- Related project: `Projects/lmf-rpg-subscreen.md`
