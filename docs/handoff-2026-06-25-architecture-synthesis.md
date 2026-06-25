# Architecture Synthesis — Handoff Brief

**Date:** 2026-06-25
**Produced in:** Claude Code **web** session (claude-opus, architect role)
**Baseline read:** `lmf` repo @ `29bf8c9` (branch `claude/confident-hypatia-35d9z3`), clean tree
**For:** a cold Claude Code **terminal** session that will be grounded in the live Marlin instance
**Author note:** Jared (operator) — not a coder; sysadmin leveraging Claude Code. Evaluate everything in sysadmin primitives: *where does state live, can I `cat` it, does it survive a restart, what's the recovery artifact.*

---

## 0. How to read this doc

This is a **synthesis scaffold**, not a verdict. Its job is to separate **what exists** (observed) from **what should** (recommended), and to mark every claim's epistemic basis so the terminal session can collapse uncertainty against live data.

**Epistemic tags used throughout:**

| Tag | Meaning |
|---|---|
| `[KNOWN]` | Directly observed in the `lmf` repo @ `29bf8c9`. Cited by `file:line`. High confidence. |
| `[INFERRED]` | Deduced from observed evidence, not stated outright. Medium confidence. State the evidence. |
| `[BLIND]` | Depends on the live instance, runtime, or sibling repos I could **not** see. Unverified. Must check. |
| `[STRATEGIC]` | A judgment/recommendation, not a fact. Jared's call, not mine. |

> **Load-bearing caveat.** This brief was written from the **framework repo only**. I could not see the live Marlin vault, the `~/.lmf/` runtime, the running orchestrator, or the sibling repos (`lmf-ollama-obsidian`, `cockpit`, `marlin`, `the-time-factory`). **Every recommendation below may already be solved, partially solved, or deliberately rejected in the live instance.** Treat them as hypotheses to test, and kill any that the live data contradicts.

---

## 1. Visibility boundary

**Could see** `[KNOWN]`: the `lmf` umbrella repo — `spec/` (covenant, principles, vocabulary, vault stub, 25 ADRs, frames), `features/` (panels/skills/services/schema catalogs + specs), `stack/lmf/` (orchestrator, build_prompt, backends, vault_io), `init/`, `layouts/`, `profile/`, README.

**Could NOT see** `[BLIND]`:
- The live vault at `~/Documents/Obsidian/Marlin/` `[INFERRED path, ADR-025]` — profile, notes, skills, actual structure.
- The `~/.lmf/` runtime, installed packages, real `config.yaml`, `installed-lock.json`, `.mcp.json`.
- The running orchestrator process and its **subclass** — base `Orchestrator` sets `fresh_context = False` and notes it is "set True by subclasses" `[KNOWN: orchestrator.py:224]`. The subclass that actually runs lives in `lmf-ollama-obsidian` `[BLIND]`. **This means I do not know whether the manifest/awareness system is even active in production, or how it behaves there.**
- Sibling repos: `cockpit` (frontend), `marlin` (surfacing engine), the runtime. The *running system* is mostly out of view; "runtime is thin" claims are repo-relative, not system-wide.

The blindness is the Covenant working as designed (Term 1): the web sandbox cannot reach the sovereign space.

---

## 2. The shape diagnosis (core synthesis claim)

**Claim** `[STRATEGIC]`: LMF is violating its own ordering principle — *"Build for the Specific Population; Generalization Is Downstream"* `[KNOWN: principles.md]`. The **general** (agnostic vocabulary, five trust profiles, extensions/dispatch/domain-experts, "deploys without Jared") has run ahead of the **specific** (one exobrain that demonstrably closes loops).

**Evidence basis:**
- Vocabulary names extensions, dispatch, domain experts, role archetypes, VAULT.md derivation `[KNOWN: vocabulary.md]` — none of which have runtime support **in this repo** `[KNOWN]` / unknown in siblings `[BLIND]`.
- VAULT.md is self-described "Stub — fields named, design incomplete" `[KNOWN: vault.md:3]`.

**What this claim depends on that I can't see** `[BLIND]`: if `marlin`/`cockpit`/runtime are substantial, the "thin runtime" framing softens. The *vocabulary-outran-runtime* point still holds because the vocabulary lives here and names things no sibling could yet implement (VAULT.md→adapter derivation, dispatch).

---

## 3. Load-bearing and correct — do not touch `[KNOWN]`

- **Doctrine stack** (Covenant → Principles → Vocabulary → Frames). Tight, self-reinforcing, genuinely original. The actual product.
- **Vault-as-flat-files.** Best decision for the target neurology: object permanence you can `cat`/`grep`/`git log`/thumbdrive.
- **ADR-025** (vault/repo separation). Cleanest record in the set; reasons in state/recovery/symlinks — sysadmin-native.
- **The *concept* of manifest awareness** — a working-memory model is the right prosthetic. (The *implementation* is a reset candidate; see §4.1.)

---

## 4. The resets — "what exists vs. what should," with verify-checks

Each row: observed reality → recommendation → **the specific live-data check** that confirms or kills it.

### 4.1 Awareness state → filesystem

| | |
|---|---|
| **Exists** `[KNOWN]` | Awareness (pinned/active/stale/dismissed), turn counter, eviction, budget all live in **process memory** — `self.awareness` dicts, `orchestrator.py:226-236`, aged in `_age_awareness` (`:328`). Budget couples to `OLLAMA_NUM_CTX` (`:231,:363`). Lost on restart; not `cat`-able; doesn't travel with the vault. |
| **Should** `[STRATEGIC]` | Re-found working-memory state on the filesystem (`.awareness/` dir, or frontmatter on notes). Persistent, inspectable, portable, model-agnostic, survives restart. Compare to **Letta/MemGPT**'s self-editing memory before designing. |
| **May already be solved? VERIFY** `[BLIND]` | (a) Is the manifest system even **on** in prod? → live `config.yaml` `awareness:` block + `grep -rn fresh_context` in `lmf-ollama-obsidian`. If `fresh_context` is False in prod, this whole reset is **moot**. (b) Does the live **subclass** already persist awareness to disk? → inspect the subclass; `ls -la <vault>/.awareness/ 2>/dev/null`. If yes, **already solved** — close it. |

### 4.2 VAULT.md → build the derivation or demote the claim

| | |
|---|---|
| **Exists** `[KNOWN]` | Vocabulary states adapters (CLAUDE.md/opencode.md/AGENTS.md) are **derived** from VAULT.md (`vocabulary.md:81-82`). VAULT.md is a stub (`vault.md`). No generator in this repo. So the spec claims a pipeline that isn't here. |
| **Should** `[STRATEGIC]` | Either build VAULT.md→adapter generation, or demote the claim to "one input among several." The current state is a load-bearing inaccuracy in your own map — worst case for trust in the spec. |
| **May already be solved? VERIFY** `[BLIND]` | `cat <vault>/VAULT.md` (does a real one exist?). `find ~/.lmf ~/git/lmf -iname '*adapter*' -o -iname '*vaultgen*'` (generator?). Check whether the live `CLAUDE.md` carries a "generated from VAULT.md" marker or is handwritten. If a generator exists in a sibling, **already solved** — and the fix is just to update the framework spec to say so. |

### 4.3 Vocabulary → status dimension (built / partial / planned)

| | |
|---|---|
| **Exists** `[KNOWN]` | Vocabulary reads as a description of a system that exists; much describes intent. **Partial counter-evidence:** the registries DO carry status — e.g. `panel.rpg ... status: Planned` (ADR-023 / `features/panels/registry.json`). So status-tracking exists at the **feature** layer, just not reflected in the **vocabulary** doc. |
| **Should** `[STRATEGIC]` | Add a status column to the vocabulary (or cross-link the registry status). Converts an over-promise into an honest map — Term 3 (behavioral trust) applied to the spec itself. |
| **May already be solved? VERIFY** `[BLIND]` | Low stakes. Check whether you already track built-vs-planned somewhere central (a project board, a status note in the live vault). If so, the fix is just to surface it from the vocabulary. |

### 4.4 Invert the ordering — consolidate to "make my exobrain work, extract framework later"

| | |
|---|---|
| **Exists** `[INFERRED]` | Effort distribution (rich spec, thin in-repo runtime) suggests general-before-specific. |
| **Should** `[STRATEGIC]` | Declare Marlin-for-Jared the only thing that must fully work for the next stretch; extract the framework from it rather than designing ahead. Doctrinally correct per Term 9 + specific-first principle. |
| **This isn't a verify — it's a decision** | The only "data" that settles it is whether the live instance **actually serves you day-to-day**. That's yours to judge. See §6. |

**Smaller, mechanical** `[KNOWN]` (verify still applies — siblings may differ):
- ARIEL hardcode: `build_prompt.py:21` (`IDENTITY_PATH = "System/Memory/ARIEL.md"`) and `orchestrator.py:50` (`"Ariel wants to ..."`) ignore the config's `ai_name` (`orchestrator.py:487`). Instance name leaking into the agnostic stack (Term 2/7). *Verify:* the live runtime subclass may already override these.
- Budget heuristic coupled to `OLLAMA_NUM_CTX` — portability debt once a non-Ollama backend is primary.
- HEAD has two near-duplicate commits (`29bf8c9`, `42e9a2c`) — possible botched squash; clean before stacking more.

---

## 5. The wild landscape — "what exists out there" `[KNOWN as of ~mid-2025 cutoff; may be stale]`

LMF is a synthesis sitting at the intersection of movements that mostly don't talk to each other. No single thing *is* LMF; every *layer* has a strong analogue.

| Layer | Closest in the wild | Why it matters to LMF |
|---|---|---|
| Plain-text substrate | Obsidian; **org-mode/org-roam** | Org has done plain-text TODO/agenda/capture for ~20y — study to avoid reinventing surfacing. |
| AI-over-your-notes | **Khoj** (self-host, model-agnostic) | Closest single project to the AI layer; Knowledge Loom ≈ a focused version of its grounding piece. |
| Memory / working-set | **MemGPT / Letta**, mem0 | Closest to the §4.1 problem (self-editing tiered memory). Read before re-founding awareness. |
| Sovereignty ethos | Ink & Switch **"Local-first software"**; **Home Assistant** | The intellectual root of Covenant 1–2; HA is the structural/governance template (local, config-driven, community add-ons, proven to scale). |
| Agent/skill/tool conventions | **MCP**, Anthropic **Agent Skills** (SKILL.md), AGENTS.md/CLAUDE.md | You already ride these — you're on a live standard, not a private island. |
| ND-first framing | **Goblin.tools**, Amazing Marvin; AT "cognitive prosthetic" literature | Least company. Spirit-aligned but cloud/clinical, not sovereign. |

**Synthesis claim** `[STRATEGIC]`: every *layer* is well-trodden; the *synthesis* is not. The ND-first stance + local-sovereign/plain-text/model-agnostic substrate + serious AI-memory architecture + an explicit **Covenant** (a 9-term architectural tiebreaker — I've seen nothing like it) is the original core. **Corollary:** the maturity of the plumbing is an argument for consolidation — *adopt, don't reinvent*; spend scarce attention on the irreplaceable parts.

---

## 6. Grounding checklist for the terminal session

Goal: collapse the `[BLIND]` items into `exists`/`gap`. **Skeleton + runtime state, not private note contents** (Covenant-clean; structure reveals shape without reading the brain). Suggested reads — adjust paths to reality:

1. **Profile:** `cat <vault>/LOCAL_MIND_FOUNDATION.md` — the cognitive self-model; trust profile; active features.
2. **Vault shape:** `find <vault> -maxdepth 2 -type d` + rough file counts per dir. Populated or aspirational? Matches spec's imagined structure?
3. **Runtime:** `ls -la ~/.lmf/`; `cat <vault>/installed-lock.json` (installed vs. catalog); the real `config.yaml` (backends, **`awareness:` block** — is `fresh_context` on?); `cat <vault>/.mcp.json` (is Loom actually wired?).
4. **Skills actually deployed:** `ls <vault>/System/Skills/` vs. `features/skills/catalog.json`.
5. **Is the manifest system live?** If the orchestrator is up: `curl localhost:8742/status` and `/focus`. Resolves §4.1(a) directly.
6. **Awareness persistence?** Inspect the live orchestrator **subclass** + `ls -la <vault>/.awareness/ 2>/dev/null`. Resolves §4.1(b).
7. **VAULT.md reality:** `cat <vault>/VAULT.md` + search siblings for an adapter generator. Resolves §4.2.
8. **Vault git story:** `git -C <vault> log --oneline -10` — did ADR-025's separation actually land?

Map each result back to the matching §4 row; mark **exists / partial / gap**. That diff is the first-class "what exists vs. what should" synthesis.

---

## 7. Open decisions — Jared's calls, not the assistant's

1. **The consolidation fork** (§4.4): altitude-one ("make my exobrain work, extract framework later") vs. hold framework altitude. Recommendation `[STRATEGIC]`: consolidate. But it's a *what-did-Jared-intend* call.
2. **The awareness Covenant question:** is turn-based salience aging an "inference that breaks trust," or transparent saliency the operator can always override? My read: survives *because* visible + reversible — but you should rule it explicitly in the (currently missing) awareness ADR.
3. **Each "may-already-be-solved" item** (§4.1–4.3): confirm or kill against the live data above.

*This is a working artifact on a feature branch — keep, relocate, or delete as repo hygiene dictates. It is not framework spec.*
