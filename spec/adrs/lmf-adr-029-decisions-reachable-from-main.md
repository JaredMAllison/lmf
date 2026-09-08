---
title: "LMF-ADR-029: A decision is in force only when reachable from main"
type: adr
project: LMF
status: accepted
date: 2026-09-08
tags: [adr, lmf, doctrine, retrieval, governance, reachability]
author: Claude von Marlin
---

## Context

LMF requires every session to search prior decisions **before the first design
sentence**. That mandate is not hygiene. It exists because the operator cannot
reliably check whether he has already solved something — that is the disability
the exobrain offsets. An assistant that designs before searching manufactures the
exact rediscovery loop the system was built to prevent.

On **2026-09-08** the same defect surfaced three times in one session, in three
different forms:

1. **The retrieval tool itself was unreachable.** `scripts/adr-search.py` — which
   both `~/.claude/CLAUDE.md` and the Marlin vault `CLAUDE.md` order every session
   to run — existed only on `feat/adr-retrieval-at-decision-time`, unmerged since
   2026-08-19. The mandated path resolved to nothing. The script had to be
   extracted with `git show` twice that day purely to satisfy the rule requiring
   it.

2. **Fixing that did not fix the invocation.** The mandate named
   `~/git/lmf/scripts/adr-search.py`, a **working-tree** path, in a repo whose
   checkout habitually sits on a feature branch. Merging the script to `main` left
   the documented command still broken, because the tree was on
   `001-chrome-theme-swap`, cut before the script existed.

3. **Doctrine already being cited was unreachable.** `lmf-adr-027` and
   `lmf-adr-028` existed only on `docs/extension-access-model`. The Marlin vault's
   `Projects/athenaeum.md` cites ADR-028 as settled law — *"ADR-028 retired MUSV as
   a vault type"* — and reasons from it. Meanwhile `adr-search.py` reads via
   `git show main:`, so it was **structurally blind to both**, and the `lmf-adr-022`
   and `lmf-adr-025` it did return were the superseded versions.

### The shape

In all three the decision **existed**, was **correctly cited**, and was **not
reachable by the retrieval path**.

Nothing errored. That is the whole problem. A search that cannot see a document
does not report an omission — it returns a shorter list and reports success. And
a short list is indistinguishable from *"no prior work exists"*, which is exactly
the answer that licenses designing from scratch.

### Why this is a new axis

It is not the **Schism** ([[marlin-adr-043]]): no data was lost, corrupted, or
deleted. Every file was intact in git the whole time.

It is not a **citation** defect ([[marlin-adr-064]]): every reference carried its
namespace correctly.

It is not a **duplication** defect ([[lmf-adr-026]]): there were no copies to
drift. If anything the opposite — one canonical file, parked out of reach.

Integrity, naming, and uniqueness were all satisfied. **Reachability** is a fourth
property, and nothing governed it.

## Decision

**`main` is the reachability boundary. A decision is in force only when its
canonical file is reachable from `main`.**

Five consequences of that, stated so they can be checked:

1. **An unmerged decision is a draft**, however complete the file and however
   confidently it is cited elsewhere. Completeness is not force.

2. **Citing a decision asserts it is reachable.** If you cite an ADR that is not
   on `main`, that is a defect to surface to the operator — not to route around by
   reading it off a branch.

3. **Doctrine is read from `main`, never the working tree.** Tools and mandates
   address it as `git show main:<path>`. A working-tree path in a mandate is a bug,
   because the tree is routinely on a feature branch behind `main`.

4. **An ADR branch is finished at merge, not at commit.** Writing an ADR includes
   landing it. Parking doctrine on a branch is indistinguishable, to every future
   reader and every retrieval, from not having written it.

5. **A retrieval hit whose only home is an unmerged branch or a working tree is a
   finding**, reported as such — never silently used as though it were in force.

## Consequences

**Enables.** `adr-search` output becomes trustworthy as a *completeness* claim
rather than merely a *relevance* one. "The search found nothing" can be acted on,
which is the entire point of running it before designing.

**Forecloses.** *"The ADR exists, it is just on a branch"* stops being a defence.
So does deferring a merge because the surrounding work is unfinished — the
decision merges even when its implementation does not.

**Trade-off.** This raises the cost of writing an ADR: it is not done until it is
merged, so an operator mid-thought cannot park doctrine indefinitely. That cost is
accepted. The alternative is a retrieval system that under-reports silently, which
is worse than no retrieval system, because it produces false confidence that prior
work was checked.

**Fragility named honestly.** Nothing mechanically prevents citing an unreachable
decision at the moment of writing. The check below is run on demand, not enforced
at write time. Automating it — extending `adr-search.py` to flag hits absent from
`main` — is a candidate, deliberately not built here.

**Scope.** This governs the framework's decision store and applies to any
instance. Instance-level ADR homes (`Marlin/Decisions/`, feature `adrs/`) inherit
it: reachable means reachable from that repository's own trunk.

## Compliance

Every `lmf-adr-NNN` cited anywhere in a vault must exist on `lmf` `main`. Run from
the vault root:

```bash
grep -rhoE '\blmf-adr-[0-9]{3}\b' --include='*.md' . | sort -u | while read slug; do
  git -C ~/git/lmf ls-tree main --name-only spec/adrs/ | grep -q "^spec/adrs/$slug" \
    || echo "UNREACHABLE  $slug — cited in the vault, not on lmf main"
done
```

Run against the Marlin vault on 2026-09-08 after the corrective merges: **28
distinct slugs cited, zero unreachable.** Run before those merges, it would have
flagged `lmf-adr-027` and `lmf-adr-028` — the two this ADR was written because of.

Additional checks a future reader can apply:

- No mandate in any `CLAUDE.md`, `AGENTS.md`, or `opencode.md` names a
  working-tree path for doctrine. All use `git show main:`.
- `scripts/adr-search.py` resolves from `main` regardless of which branch any
  working tree is on.

## Related

- [[lmf-adr-026-adr-governance-and-namespacing]] — one canonical file, no copies. This adds: and it must be on `main`.
- [[marlin-adr-064]] — a citation must carry its namespace. This adds: and must resolve.
- [[marlin-adr-043]] — the Schism. Distinct: that is loss, this is unreachability without loss.
