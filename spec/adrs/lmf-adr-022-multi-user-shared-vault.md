---
title: "LMF ADR-022: Multi-User Shared Vault Architecture"
type: adr
project: LMF
status: accepted
date: 2026-05-16
tags: [adr, lmf, vault, architecture, multi-user]
---

## Context

LMF has operated exclusively on single-user personal exobrain vaults — Marlin (Jared), Prosper0 (work context), Scribner (Tori's writing). Each vault has one owner and one LMF instance.

The Athenaeum (Jaina's education vault) is the first case where a knowledge vault is meaningfully shared by multiple people with different relationships to its content. Jared owns and administers it. Tori is an active co-author. Jaina is the subject — she should be able to see her world, but not modify the canonical record.

This pattern will recur. A Community Vault is the next anticipated instance. The role model needs to be canonicalized now, as doctrine, before more vaults follow.

## Decision

Introduce **Multi-User Shared Vault (MUSV)** as a first-class LMF vault type.

A MUSV has explicit roles. Three tiers are defined:

| Role | Access | Notes |
|---|---|---|
| **Admin** | Read + Write + Structural control | Owns the vault. Sets roles. Final authority on schema and organization. |
| **Contributor** | Read + Write + Own tasks | Full participant. Can create, modify, and resolve their own tasks. Cannot restructure the vault. |
| **Reader** | Read only | Can see all vault content. Cannot write. |

**Reference implementation: Athenaeum**

| Person | Role | LMF Instance |
|---|---|---|
| Jared | Admin | Marlin |
| Tori | Contributor | Scribner |
| Jaina | Reader | Deferred — no instance yet |

Jaina's Reader access is implemented through direct Obsidian access until her LMF instance is built. This is intentional deferral, not a gap.

Tori's Contributor access is initially through direct Obsidian. Tooling to route Scribner's writes into Athenaeum is a low-priority sub-project of Athenaeum.

## Consequences

**Enables:**
- LMF can now model family, community, and educational shared knowledge spaces
- Role model is reusable for Community Vault, employer vaults, and future MUSVs
- Tori's Scribner instance gains a second vault context (education) alongside her writing vault — Scribner is not single-vault by definition

**Forecloses:**
- MUSVs are not a feature of personal exobrain vaults — Marlin remains single-user. The distinction matters: a MUSV is a shared resource, not an extended personal vault.

**Trade-offs:**
- Write access without tooling means Tori writes directly in Obsidian, which bypasses any LMF capture discipline. This is acceptable short-term; tooling resolves it.
- No conflict resolution protocol yet. When Jared and Tori disagree on a curriculum entry, Admin wins by default. This is a social decision, not a technical one.

**Open questions (not resolved by this ADR):**
- How does a Contributor's LMF instance authenticate to a vault that isn't its home vault?
- Does each MUSV need its own CLAUDE.md / instance context layer?

## Compliance

- Each MUSV must have a `README.md` or `CLAUDE.md` at its root declaring roles explicitly.
- Task ownership in a MUSV is tracked by a `owner` field in task frontmatter (Jared or Tori, not just the vault).
- LMF instance configs that reference a MUSV must declare their access level (`admin` | `contributor` | `reader`).
- See [[Athenaeum]] for the reference implementation.
