---
title: "LMF-ADR-026: ADR Governance — Namespacing, Location, and Indexing"
type: adr
project: Local Mind Foundation
status: accepted
date: 2026-06-01
tags: [adr, lmf, adr-system, governance, documentation]
---

## Context

ADRs in this system span many projects — LMF, Marlin, Prosper0, Ariel von Marlin, Sol3, and more.
[[lmf-adr-005-adr-inheritance-model]] established the *inheritance* relationship (the `parent_adr`
field linking an instance decision up to its LMF parent), but never the *operational* rules: how ADRs
are named and numbered, where each project's ADRs physically live, and what the central index is for.

A full census (2026-06-01) showed the cost of leaving this implicit:
- The central index (`~/.claude/decisions/README.md`) lists dozens of ADRs that exist **nowhere on
  disk** — `marlin-adr-001`–`032` and the entire `ariel-von-marlin-adr-*` range. Readers can't tell a
  pointer-to-elsewhere from a phantom.
- The Marlin vault holds **duplicate copies** of five `lmf-adr` files (020–023, 025) whose canonical
  home is `~/git/lmf/spec/adrs/`. Two files, one decision — they will drift.
- Numbering only makes sense per-project (LMF runs 001–025; Marlin runs its own; Prosper0 its own), but
  that was never written down, so the index *looked* like one broken global sequence.

This ADR records the convention so these problems stop recurring. It is an LMF-level decision because
the ADR system is universal infrastructure all instances inherit (the same scope `lmf-adr-005` claimed).

## Decision

1. **Three levels.** Every ADR belongs to one of three levels, reflecting the scope of the architecture
   it governs. The level fixes the namespace prefix and the canonical home:
   - **LMF level (framework)** — universal decisions binding the framework and every instance.
     Prefix `lmf-adr-NNN`; home `~/git/lmf/spec/adrs/`.
   - **Feature level** — decisions scoped to a single LMF feature's own design/contract, not the whole
     framework. Prefix `<feature>-adr-NNN`; home *with the feature*, e.g.
     `~/git/lmf/features/<feature>/adrs/`. *(Newly formalized — see Reconstruction/Consequences; the
     prefix and exact home are the operator's to confirm.)*
   - **Personal level (instance)** — decisions specific to how one operator's instance is built and run.
     Prefix `<instance>-adr-NNN` (`marlin-adr`, `ariel-von-marlin-adr`); home the instance vault
     `Decisions/`.
   Legacy/other projects (`prosper0-adr-*`, `sol3-adr-*`) are Personal-level instances of this pattern,
   each homed in its own repo/vault. (Legacy `~/git/prosper0/` is superseded code; Prosper0 is a future
   work instance.)

2. **Numbering and single canonical file.** `NNN` is sequential **within each namespace only** — there
   is no global sequence (`lmf-adr-026` and `marlin-adr-026` are unrelated). Each ADR lives in **exactly
   one** canonical file at its level's home — **no copies.** Cross-level/cross-project references use
   **wikilinks + the index**, never a duplicated file. (The vault copies of `lmf-adr-020`–`023`/`025`
   are drift hazards slated for de-duplication.)

3. **Inheritance** is governed by [[lmf-adr-005-adr-inheritance-model]]: a lower-level ADR declares
   `parent_adr` when it implements a higher-level decision. The chain runs **Personal → Feature → LMF**
   — a Personal ADR may inherit from a Feature or LMF ADR; a Feature ADR may inherit from an LMF ADR. A
   lower level may narrow or specialize a higher decision but cannot contradict it without the parent
   being updated or superseded first.

4. **The central index** (`~/.claude/decisions/README.md`) is a cross-project **pointer/map, not a
   store.** An entry may point at an ADR that lives in another repo. The index must track disk reality:
   an entry whose file exists nowhere is a bug — remove it or recover the file. The index is never the
   source of truth for an ADR's content.

5. **Lifecycle** (consolidated from the global CLAUDE.md, recorded here as doctrine):
   - Template: `Marlin/Decisions/_template.md` (title · date · status · context · decision · consequences).
   - Status ∈ {`proposed`, `accepted`, `deprecated`, `superseded`}.
   - Any significant, non-obvious decision gets an ADR proactively — especially where the obvious
     alternative was consciously rejected.
   - Reversing a decision marks the original `superseded` with a link to its replacement.

## Consequences

**Enables:** unambiguous numbering across projects; a reader can locate any ADR from its prefix alone;
the index becomes a trustworthy map; duplication and drift are named and bannable.

**Forecloses:** a single global ADR sequence; ad-hoc placement; the "index is the source of truth"
assumption.

**Trade-offs:** a one-time reconciliation is still required (remove phantom index entries, de-duplicate
the vault's `lmf-adr` copies, recover or retire any genuinely-lost `marlin-adr`s). That cleanup is
tracked separately; this convention prevents recurrence but does not auto-repair history. As with
`lmf-adr-005`, the field/location rules are conventions, not machine-enforced constraints.

**On the Feature level (newly formalized 2026-06-01):** the LMF and Personal levels already existed in
practice; the Feature level is the operator's explicit addition. Feature-scoped decisions previously
landed in LMF or Personal ADRs by default. A future pass should identify those (e.g. Feature Manager,
sos_gateway, rupture-detector internals) and decide which to migrate to feature-level ADRs. The exact
prefix and home (`<feature>-adr-NNN` under the feature dir) are proposed here and open to the operator's
confirmation before backfilling.

## Compliance

A future reader verifies this is being followed by checking:
- Every ADR filename matches `<project>-adr-NNN-short-title.md`.
- `find ~ -iname "*-adr-*.md"` (excluding `.worktrees/`) shows exactly one canonical file per ADR — no
  cross-location duplicates.
- Each index entry resolves to a real file in that project's canonical location.
- Instance ADRs that implement an LMF decision carry a `parent_adr` field (per `lmf-adr-005`).
