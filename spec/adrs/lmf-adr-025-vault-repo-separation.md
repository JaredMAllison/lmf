---
title: "LMF-ADR-025: Vault/Repo Separation"
type: adr
project: Local Mind Framework
status: accepted
date: 2026-05-21
tags: [adr, lmf, vault, architecture, git, sovereignty, installation]
---

## Context

LMF framework code (`features/`, `stack/`, `spec/`, `docs/`, `layouts/`) has been co-located inside the reference operator's personal vault directory (`~/Documents/Obsidian/Marlin/`), which was also a git checkout of `JaredMAllison/lmf.git`. Personal vault files were gitignored, but two incidents occurred: `git stash` wiped personal vault files, and vault skills were lost during recovery.

The deeper problem: co-location conflates two distinct things. The vault is the operator's second brain — personal notes, tasks, projects, insights. The LMF repo is a shared framework — specs, catalog, runtime, feature definitions. Keeping them in the same directory means any git operation on the framework runs inside the space where personal files live.

A secondary problem: a new operator cannot "install LMF" without receiving a clone of the reference operator's vault structure. There is no clean separation between "what is the framework" and "what is Jared's personal instance."

The question this ADR resolves: **where does LMF live relative to the operator's vault?**

## Decision

LMF operates across three distinct layers, each with its own home:

**1. Framework** (`~/git/lmf/` or wherever the operator clones it)  
The `JaredMAllison/lmf.git` repo. Contains specs, catalog, Feature Manager, schemas, init wizard, and runtime code. Shared, upgradeable, not operator-specific. Development and contributions happen here.

**2. LMF runtime** (`~/.lmf/`)  
The operator's LMF home directory. Contains installed packages, the install workspace, and a symlink to the lock file. Not a git repo.

`~/.lmf/installed-lock.json` is a symlink. The real file lives at the vault root (`<vault>/installed-lock.json`) so that a single vault backup or thumbdrive pull contains everything needed for recovery. The init wizard creates the symlink. On recovery to a new machine or path, the symlink is re-created pointing at the restored vault location — one step, trivial.

**3. Vault** (operator's Obsidian vault, wherever they keep it)  
The operator's personal second brain. Contains personal notes only, plus two bridge files (`CLAUDE.md` and `.mcp.json`) that connect the vault to LMF. The vault is NOT a checkout of `lmf.git`. It has its own independent git and sync story.

### New operator install flow

```
git clone https://github.com/JaredMAllison/lmf.git ~/git/lmf
python ~/git/lmf/features/feature_manager/manager.py init
```

The init wizard asks for the vault path and assistant name, installs baseline features to `~/.lmf/`, drops `CLAUDE.md` and `.mcp.json` into the vault root, creates `<vault>/installed-lock.json`, and symlinks `~/.lmf/installed-lock.json` to it. The operator's vault never becomes an LMF git checkout.

### Backup surface

| What | Backed up where |
|---|---|
| Personal vault content | Vault (git + Syncthing) |
| `installed-lock.json` | Vault root (real file, tracked in vault git) |
| LMF framework | Not backed up — public repo, re-cloneable |
| Package workspace | Not backed up — re-installable from lock file |

A thumbdrive pull of the vault is a complete recovery artifact. Recovery on a new machine:
```
1. Restore vault
2. git clone https://github.com/JaredMAllison/lmf.git ~/git/lmf
3. ln -s <vault>/installed-lock.json ~/.lmf/installed-lock.json
4. lmf install --from-lock
```

The symlink path changes on recovery; the lock file contents do not. Step 3 is the only path-aware operation.

### Baseline (auto-installed)

Knowledge Loom MCP, operator profile scaffold, CLAUDE.md bridge. All other features are opt-in.

## Consequences

**Enables:**
- git operations on the LMF framework repo cannot affect personal vault files — they are in different directories
- New operators install a clean framework without receiving any reference operator content
- The vault is a self-contained recoverable artifact: personal notes + bridge files, nothing else
- Framework can be updated independently of any operator's vault

**Forecloses:**
- LMF framework code living inside the vault (by convention or gitignore) — this is now structurally prohibited
- Any git operation that could stash, clean, or checkout personal vault content as a side effect of framework work

**Trade-offs:**
- Operators must keep `~/git/lmf/` (or equivalent) up to date separately from their vault. This is intentional: framework upgrades are deliberate, not automatic.

### Sovereignty concession (reference implementation)

The Marlin reference implementation pushes vault content to a GitHub private remote as a temporary file safety measure, pending a proper BDR (Backup/Disaster Recovery) implementation. This is a deliberate concession of Local Sovereignty (Covenant Term 1), accepted explicitly and noted here so future operators understand the trade-off being made.

## Doctrine alignment

- **Covenant Term 1 (Local Sovereignty):** Vault content remains operator-owned. GitHub remote is a noted sovereignty trade-off, accepted explicitly.
- **Covenant Term 7 (Contribute Upstream):** "Customizations live in the vault layer." Confirmed: CLAUDE.md and operator profile are vault-resident. Framework improvements go to `lmf.git`.
- **ADR-021 (Portability):** Vault as self-contained recovery artifact is strengthened — it now contains only personal notes and bridge files, with no framework dependencies embedded.
- **Feature Manager:** Lock file default (`~/.lmf/installed-lock.json`) already pointed to this architecture. This ADR makes the intent explicit.
