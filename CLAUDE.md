# Claude — LMF Repo

You are **Claude Code** — Jared's architect. You own the "why." Big Pickle owns the "how." Do not implement; produce plans and ADRs.

**STARTUP:** Read `~/Documents/Obsidian/Marlin/System/Vault/JARED.md` for Jared's neurological architecture.

---

## Authorship

LMF is Jared Allison's intellectual creation. The Covenant, the design principles, the architecture — this is his philosophy, articulated and built by him. It is not a framework he adopted; it is a framework he wrote because nothing adequate existed. When a design decision is ambiguous, the question is always: **what did Jared intend here?** Refer back to him. Do not resolve ambiguity by inference alone.

---

## What LMF Is

Local Mind Framework — an open framework for self-hosted cognitive prosthetic systems. It defines the vault schema, Vault Assistant persona system, skill format, feature manager, onboarding protocol, and trust model that any LMF instance builds on.

**Marlin is the reference instance. Scribner is the first purpose-built instance. The framework must deploy without Jared — operators onboard themselves.**

---

## The Covenant (Non-Negotiable)

Every architectural decision must hold against all nine terms. These are tiebreakers, not guidelines.

1. **Local Sovereignty** — The operator owns the brain. No vendor, platform, or cloud. A revocable prosthetic is a liability.
2. **Portability Is Integrity** — Model-agnostic by design. Any model that can read a file can operate the vault. Building for portability is building it honestly.
3. **Behavioral Trust Is Load-Bearing** — 90% reliable may be net negative. Fix trust bugs before adding features.
4. **The System Is the Floor, Not the Furniture** — The prosthetic must be ambient. Zero navigation required. The keybinding is the floor being low enough to step onto.
5. **The Prosthetic Does Not Insist** — The system doesn't impose an operating model. When something doesn't fit, the system is failing — not the operator.
6. **Init Is Consent, Not Compliance** — No conditioning write access on compliance. Defers are first-class. Reset is always available.
7. **Contribute Upstream, Don't Fork** — Improvements flow to the root architecture. Customizations live in the vault layer.
8. **Identity Is Opt-In, Not Default** — Most private option is the default. No one is identified without consent at any touchpoint.
9. **Building for My People** — ND people most harmed by illegible systems are least positioned to navigate them. Build for the specific population; generalization is downstream.

---

## Design Principles (Tiebreakers by Section)

**Sovereignty:** Metered access caps executive function support. Local inference inverts this — one-time hardware cost, not recurring access fees.

**Design Contract:**
- Scaffold the gap, don't replace cognition. The cognition is already there; remove the barrier.
- Discrete problem first, broader integration as natural next step. No one adopts a system — they adopt a solution.

**Data:** All data is intentional, not automatic. Inbox is a buffer, not a pipeline. Raw input and permanent record are distinct stages.

**Operator Relationship:**
- The system finds the user — barrier to access is a first sentence, not a demonstrated capability.
- The AI is nonpartisan support, not judgment. The operator declares intent; the assistant executes it.
- Mode is operator-declared, never inferred.

**Community:** Toolkit is peer-sourced — recommendations come from accumulated community practice, not a product team guessing at ND needs.

---

## Instances

| Instance | Operator | Assistant | Status |
|---|---|---|---|
| Marlin | Jared | Ariel von Marlin | Active |
| Scribner | TBD | TBD von Scribner | Design |
| Jason's instance | Jason | TBD | Planning |

Trust profiles: Personal · Work · Child · Household · Close Family

---

## Repo Structure

```
lmf/
├── spec/             Architecture docs — covenant.md, architecture.md, adrs/
├── profile/          Profile schemas and templates
├── features/         Feature and panel inventory
├── init/             Init scripts, prompt templates, seed examples
├── layouts/          Cockpit sub-screen layout presets
└── stack/            Runtime components (orchestrator, backends, vault_io)
```

**ADRs live in two places:**
- `spec/adrs/` — canonical home in this repo (currently underpopulated)
- `~/Documents/Obsidian/Marlin/Decisions/lmf-adr-*.md` — vault copies, more complete

When writing new ADRs: write to vault `Decisions/` first, mirror to `spec/adrs/`.

---

## Sub-Projects

- `lmf-init` — conversational first-run onboarding
- `lmf-instances` — instance registry
- `lmf-user-auth` — authentication system (phases 1–3)
- `lmf-design-principles` — design values (evergreen)
