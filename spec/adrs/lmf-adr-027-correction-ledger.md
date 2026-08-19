---
title: "LMF-ADR-027: Corrections are logged, tagged, and operator-promoted — a three-stage fitting ledger"
type: adr
project: LMF
status: accepted
date: 2026-07-30
tags: [adr, lmf, fitting, prosthetics, session-recall, feedback, alexithymia, doctrine]
---

## Context

Prosthetic fitting is **breach-triggered** ([[breach-is-the-fitting-trigger]]): the assistant records, frames, or delivers something wrong, the operator feels it and corrects, and the correction becomes structure. The loop only closes because of the **accumulation** step — seeing that this breach is an instance of a pattern across earlier ones.

**That accumulation is currently ad hoc**, and it has already failed in a demonstrable way. `feedback_vault_silence_is_not_inaction` was written 2026-07-27. On 2026-07-30 the same class of error recurred with the rule in context, and it was caught only because the operator happened to recognise it and say so. Accumulation that depends on either party *remembering* is exactly the faculty the vault exists to replace ([[the-vault-is-the-map-the-life-is-the-territory]]).

A **behavioral-inference channel** was considered as the fix — detect abandonment, latency, repeated rewrites, and infer operator dissatisfaction. **Rejected.** Inferring a reaction and handing it to the operator as theirs is the exobrain authoring a preference on their behalf, which is worse than no signal ([[feedback_exobrain_output_is_a_claim]]). A wrongly-inferred preference baked into a fit compounds silently.

Two enabling facts made a better option available. Session transcripts are **already preserved** — 58 JSONL transcripts back to 2026-07-06 — and `System/SessionRecall/` already has layers 1–2 live (SessionEnd enqueue hook, derived metadata index regenerated at close), with layer 3 (semantic digests) designed but deferred on local inference.

Separately, this bears on an accessibility question. LMF's fitting loop assumes an operator who can detect and articulate a felt reaction. Operators high in alexithymia — substantially more common among autistic people, and dimensional rather than binary — may not be able to supply that signal at all, and the loop would stall silently with no error.

## Decision

Adopt a **three-stage correction ledger**. Each stage has a different cost and a different actor.

**1. Flag (in-session, assistant-side, cheap).**
The assistant flags corrections as they occur and writes a durable record into the vault. **The assistant does the flagging, not the operator** — requiring the operator to flag their own corrections puts friction precisely at the moment of annoyance, when they have least patience for it. Being corrected is an *observable event*, not an inferred state, so this involves no mind-reading.

**Deliberately over-flag.** False positives are cheap because classification is retrospective and junk is dropped at stage 2. Under-flagging loses data permanently. Same logic as ADR-053's mandatory `Thinking/` entry.

**2. Tag (fitting session, operator-side, deliberate).**
Fitting sessions ([[behavioral-neurology-fitting]]) review the flagged set and classify it **in the operator's own vocabulary**. The tag scheme is not supplied by LMF — a fixed taxonomy would be a pre-committed fitting decision, and schemas encode the cognition that authored them. Expect early sessions to *produce* vocabulary rather than apply it.

**3. Promote (operator-gated).**
Clusters of related corrections are elevated by the operator into durable feedback (memory files, doctrine, ADRs). **No fixed threshold.** "Three corrections becomes a rule" would be a pre-committed fitting decision; the fitting session surfaces the cluster and the operator judges.

**Revocability is a first-class property.** Jared, 2026-07-30: *"The beauty is it is only as permanent as I find it useful."* Flags are droppable, tags mutable, promoted feedback deletable, demotion free at every stage. Nothing in this mechanism locks in.

**The ledger is an optimization, not the source of truth.** Corrections are ultimately derivable from the session transcripts, so a missed flag self-heals when the semantic tier reconciles against the JSONL. This is the same rule that already governs SessionRecall's enqueue queue, and it means flagging can be lossy in the moment without being lossy in the end.

**Not blocked on local inference.** Stages 1–3 are buildable now: append-only flag writes, manual review, manual promotion. The deferred semantic tier improves recall later; it is not a prerequisite.

## Consequences

**Enables:**
- Fitting accumulation becomes a **dataset rather than a memory**. The failure that prompted this ADR becomes structurally unlikely rather than dependent on recall.
- **Alexithymia accommodation with no introspection required.** Correcting demands no emotional vocabulary — an operator who cannot name a single feeling still says "no, not like that." This serves that operator by never asking how they feel, which is a better accommodation than teaching them to answer. It does not require the operator to be trained.
- **Auditable doctrine provenance.** Which corrections produced which rules becomes visible, so a future reader can see why a feedback file exists.
- Applies to any LMF instance and any operator; nothing here is Marlin-specific.

**Costs and forecloses:**
- Fitting sessions become a real recurring commitment. Without them the ledger accumulates and nothing is promoted — flags without review is a pile, not a loop.
- Over-flagging produces noise that someone must wade through.
- The tag vocabulary must bootstrap from nothing; the mechanism is weakest in its first weeks.
- Assistant-side flagging risks flagging *disagreement* as *correction*. When the operator argues rather than corrects, that is a different event; conflating them would encode capitulation as doctrine.

**Trade-off accepted:** a maintained ledger in a codebase whose stated preference is derived indexes ([[prefer-derived-indexes-over-maintained-ones]]). Mitigated by treating the ledger as an optimization over the transcripts, exactly as the enqueue queue is treated.

**Noted pattern:** this is structurally identical to [[Decisions/marlin-adr-053-longform-rigor-hierarchy]] — cheap floorless capture, retrospective classification, operator-gated promotion, free demotion. Two different problems solved with the same ladder on the same day, which suggests a reusable design pattern rather than a coincidence.

## Compliance

- ⚠️ **This file is not yet at its canonical home.** Per `lmf-adr-026-adr-governance-and-namespacing`, LMF-level ADRs live in `~/git/lmf/spec/adrs/`. This one sits in the vault pending promotion, because at time of writing the lmf repo was mid-feature on branch `001-chrome-theme-swap` with uncommitted work in `features/chrome/`, and dropping an unrelated ADR onto that branch was not appropriate. **Promote it when that branch lands.** (The vault also currently holds `lmf-adr-020`–`025`, contrary to the index's 2026-06-01 note that duplicates were removed — that drift is unresolved and not addressed here.)
- **Ledger location:** in the vault, not in `~/.claude/`. Vendor transcripts are tool-specific and outside ADR-001's durability promise; the fitting corpus must survive a change of assistant vendor ([[lmf-adr-021-instance-portability-requirement]]).
- **Promoted feedback cites its corrections.** A feedback/memory file produced by promotion should name the flagged corrections behind it, so the provenance chain is inspectable.
- **Build location:** framework logic → `~/git/lmf/features/`, not Marlin, per the LMF build doctrine. Marlin holds instance config and the ledger contents only.
- **Verification:** a future reader can check that flags are being written, that fitting sessions consume them, and that promoted feedback files carry correction provenance. **If the operator is ever asked to flag their own corrections in-session, or a fixed promotion threshold appears, this ADR is being violated.**

Related: [[breach-is-the-fitting-trigger]] · [[lmf-goal-is-fit-readiness]] · [[the-vault-as-predictive-substrate]] · [[continuous-prosthetic-fitting]] · `System/SessionRecall/README.md` · [[Quotes/only-as-permanent-as-i-find-it-useful]]
