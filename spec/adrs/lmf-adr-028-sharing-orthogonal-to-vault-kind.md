---
title: "LMF-ADR-028: Sharing Is Orthogonal to Vault Kind"
type: adr
project: Local Mind Foundation
status: accepted
date: 2026-08-19
author: "Claude von Marlin"
seed: Jared
amends: "[[lmf-adr-022-multi-user-shared-vault]]"
tags: [adr, lmf, vault, architecture, multi-user, extension, dispatch, access-model]
---

## Context

LMF carries two independent answers to "what kind of thing is a vault," and they have never been reconciled.

**ADR-022 (2026-05-16)** introduced the **Multi-User Shared Vault (MUSV)** as *"a first-class LMF vault type"* with a three-tier role model — Admin, Contributor, Reader — and named Athenaeum as the reference implementation.

**`spec/vocabulary.md`** independently defines the vault taxonomy the rest of the framework uses: `instance` versus `extension`, where extensions are `project vault` or `knowledge vault`, reached from a `home vault` by `dispatch`. MUSV does not appear in it.

Two taxonomies, no stated relationship. A vault can be typed under either and the answers do not compose.

### The stale claim

ADR-022 drew its central boundary here:

> *"MUSVs are not a feature of personal exobrain vaults — **Marlin remains single-user.** The distinction matters: a MUSV is a shared resource, not an extended personal vault."*

[[marlin-adr-050-multi-operator-exobrain]] (2026-07-14) made Tori a **full second operator on Marlin** — read and write across the whole vault, her own cockpit instance, her own `author:` provenance.

Marlin is a personal exobrain vault with two people writing to it. **ADR-022's boundary was falsified two months ago and nothing recorded it.** The seam is not a gap between two models; it is a stale claim in the older one.

### Trigger

Designing a Thirsty Sword Lesbians campaign vault where **Tori is Admin and Jared is Contributor** — the first shared vault in which Jared is not the Admin, and where the repo is hosted on Jared's account for someone else's vault. Whether that arrangement is coherent, or a doctrine violation, depends entirely on which model governs. It could not be answered without settling this.

## Decision

**Sharing is orthogonal to vault kind.** A vault has two independent properties, and MUSV is not one of them.

### 1. Kind — what the vault *is*

From `spec/vocabulary.md`, unchanged by this ADR:

| Kind | Definition |
|---|---|
| `instance` | A personal exobrain. Full binding, named assistant, init required. |
| `extension` | A vault dispatched into from a home cockpit. No binding, no named assistant, no init. Subtypes: `project vault`, `knowledge vault`. |

### 2. Access — who may do what

From ADR-022, retained in full. A table of principal → role:

| Role | Access |
|---|---|
| **Admin** | Read + Write + Structural control |
| **Contributor** | Read + Write + Own tasks |
| **Reader** | Read only |

### 3. MUSV is demoted from type to descriptor

**"MUSV" names a condition, not a kind:** a vault whose access table has more than one row. It is a legitimate adjective and an illegitimate type. Every vault has a kind and an access table; multi-user is what you observe when the table is longer than one.

### 4. Admin semantics depend on kind

This is the load-bearing rule, and it is what ADR-022 was reaching for and got wrong.

- **On an `instance`, Admin is the operator and is NOT transferable.** The Covenant governs: *the operator owns the brain*. A second principal on an instance may be Contributor or Reader, never Admin. Tori's full write access to Marlin does not make her co-owner of Jared's exobrain, and Jared cannot cease to be Marlin's operator.
- **On an `extension`, Admin IS transferable, and need not be whoever hosts it.** An extension carries no binding, no bound assistant, and no exobrain. Ownership is custody of a workspace.

ADR-022 declared instances unshareable when what it needed was to declare instance-Admin unmovable. The corrected rule permits ADR-050's reality and forbids what ADR-022 was actually protecting against.

### 5. Extensions are standalone; home vaults reference, never contain

An extension is *visited from* a home vault. When two operators dispatch into the same extension from different home vaults, the extension belongs to neither.

Nesting an extension inside a home vault's directory tree is **forbidden**, on two concrete grounds:

- **Wikilink namespace collision.** Obsidian resolves `[[Link]]` within the vault root. Shared vaults use deliberately generic node names — Athenaeum's most-linked notes are `Math`, `Science`, `Health`. Nesting makes those resolve to the wrong vault's notes.
- **Nested repositories.** A vault inside a vault is two git repos, one swallowing the other absent a `.gitignore` maintained forever.

### 6. The reference mechanism is the project handle

[[marlin-adr-058-external-vault-project-handles]] already specifies it: every project involving an external vault gets a handle in the home vault's `Projects/`, recording identity, status, boundaries, and links, without duplicating content.

**ADR-058's handles are the extension registry.** No new registry is to be built. A `vault_path` field on the handle is sufficient for a cockpit to derive its dispatch list.

### 7. Reader access does not require an instance

**A Reader is satisfied by read-only dispatch into an extension.** Dispatch is task-scoped orientation, not binding; it requires no init, no named assistant, and no exobrain.

This supersedes ADR-022's rationale for deferring Jaina's access:

> *"Jaina's Reader access is implemented through direct Obsidian access until her LMF instance is built. This is intentional deferral, not a gap."*

The deferral was an artifact of assuming access implies an instance. Under this ADR it is a write-gate setting and a handle entry.

### 8. Custody is not Admin

Hosting an extension's repository or disk is a **service**, transferable at any time, and confers no structural authority. Repo owner and vault Admin are separate roles and may be different people.

## Consequences

**Enables:**

- **Athenaeum retypes cleanly** as a `knowledge vault` — the vocabulary entry reads *"may be managed on behalf of a beneficiary who isn't the primary operator,"* written for this case.
- **Jaina's Reader access unblocks** without building a child an exobrain.
- **Tori-as-Admin on a project vault is coherent**, with a stated reason rather than an intuition.
- **Marlin's two-operator reality becomes expressible**: `instance`, Jared Admin (non-transferable), Tori Contributor.
- The extension registry problem is closed by work already done.

**Forecloses:**

- MUSV as a vault type.
- Transferring Admin on an instance.
- Nesting extensions inside home vaults ("absorbing" a shared vault into a personal one).

**Trade-offs:**

- ADR-022 is **amended, not superseded.** Its role vocabulary survives intact and is load-bearing here; its type claim and its instances-are-unshareable boundary do not.
- Documents asserting Athenaeum is "the first MUSV" need updating: `Projects/athenaeum.md` and `Athenaeum/CLAUDE.md` in the Marlin vault.
- `Projects/community-vault.md` is scoped as a future MUSV; it becomes a shared extension.
- Like ADR-005 and ADR-026, these are conventions, not machine-enforced constraints.

**Open questions — explicitly not resolved here:**

- **`spec/vault.md` is a stub** (*"fields named, design incomplete"*). Every extension needs a `VAULT.md`, and the schema plus the VAULT.md → vendor-adapter derivation pipeline are undesigned. Athenaeum and Marlin both have a `CLAUDE.md` with no agnostic source, inverting the stated derivation direction.
- **Dispatch is unimplemented.** `~/git/cockpit/cockpit.py:20` holds a single module-level `VAULT` from `VAULT_PATH`; one cockpit instance serves exactly one vault. The vocabulary describes dispatch; nothing performs it.
- **Write-gate enforcement of the Reader role is unspecified.** Item 7 is sound in doctrine and has no mechanism yet.

## Compliance

A future reader verifies this is being followed by checking:

- No document describes a vault type called "MUSV." Vaults are typed `instance`, `project vault`, or `knowledge vault`, with a separate access table.
- No vault declares a non-operator as Admin of an `instance`.
- No extension's directory sits inside a home vault's tree.
- Every extension in active use has a handle in its operators' home vaults per ADR-058.

**Applied on 2026-08-19:** this ADR only. Athenaeum's retyping, the ADR-022 amendment note, and the community-vault rescope are owed and not yet done.

## Related

[[lmf-adr-022-multi-user-shared-vault]] (amended) · [[lmf-adr-001-local-mind-foundation-architecture]] · [[lmf-adr-006-instance-trust-profiles]] · [[lmf-adr-021-instance-portability-requirement]] · [[lmf-adr-023-rpg-vault-schema]] · [[lmf-adr-025-vault-repo-separation]] · [[lmf-adr-026-adr-governance-and-namespacing]] · [[marlin-adr-050-multi-operator-exobrain]] · [[marlin-adr-058-external-vault-project-handles]] · `spec/vocabulary.md` · `spec/covenant.md`
