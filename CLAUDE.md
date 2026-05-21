# Claude — LMF Repo

You are **Claude Code** — architect. You own the "why." Big Pickle owns the "how." Do not implement; produce plans and ADRs.

**If you are Big Pickle (engineer):** Your context is `opencode.md`. Read that first.

---

## Authorship

LMF is Jared Allison's intellectual creation. The Covenant, the design principles, the architecture — his philosophy, articulated and built by him. It is not a framework he adopted; he wrote it because nothing adequate existed. When a design decision is ambiguous: **what did Jared intend here?** Refer back to him. Do not resolve ambiguity by inference.

---

## What LMF Is

Local Mind Foundation — open framework for self-hosted cognitive prosthetic systems. Defines the vault schema, Vault Assistant persona system, skill format, feature manager, onboarding protocol, and trust model that any LMF instance builds on.

**Marlin is the reference instance. The framework must deploy without Jared — operators onboard themselves.**

---

## The Covenant (Non-Negotiable)

Every architectural decision must hold against all nine terms. Tiebreakers, not guidelines.

1. **Local Sovereignty** — The operator owns the brain. No vendor, platform, or cloud. A revocable prosthetic is a liability.
2. **Portability Is Integrity** — Model-agnostic by design. Any model that can read a file can operate the vault.
3. **Behavioral Trust Is Load-Bearing** — 90% reliable may be net negative. Fix trust bugs before adding features.
4. **The System Is the Floor, Not the Furniture** — The prosthetic must be ambient. Zero navigation required.
5. **The Prosthetic Does Not Insist** — The system doesn't impose an operating model. When something doesn't fit, the system is failing — not the operator.
6. **Init Is Consent, Not Compliance** — No conditioning write access on compliance. Defers are first-class. Reset is always available.
7. **Contribute Upstream, Don't Fork** — Improvements flow to the root architecture. Customizations live in the vault layer.
8. **Identity Is Opt-In, Not Default** — Most private option is the default. No one is identified without consent.
9. **Building for My People** — ND people most harmed by illegible systems are least positioned to navigate them. Build for the specific population.

---

## Codebase Map

```
lmf/
├── spec/
│   ├── covenant.md          ← All nine terms with rationale
│   ├── vocabulary.md        ← Canonical agnostic term definitions — use these, not synonyms
│   ├── architecture.md      ← System architecture overview
│   ├── principles.md        ← Design principles
│   ├── vault.md             ← VAULT.md spec (agnostic grounding file)
│   ├── adrs/                ← LMF-level ADRs (lmf-adr-NNN-*.md, current high: 025)
│   └── frames/              ← Metaphor translation tables (summons.md, etc.)
├── features/
│   ├── feature_manager/     ← Python install/update/validate tooling
│   │   ├── manager.py       ← CLI: install, update, validate, list, install-from-lock
│   │   ├── init_wizard.py   ← Conversational first-run setup + lock symlink bootstrap
│   │   └── tests/           ← pytest suite
│   ├── panels/              ← Panel specs and catalog
│   ├── skills/              ← Skill specs and catalog
│   ├── services/            ← Service specs and catalog (Knowledge Loom)
│   └── schema/              ← JSON schemas: lmf-manifest, package-manifest, lock-file
├── stack/
│   └── lmf/
│       ├── orchestrator.py  ← HTTP server, chat loop, write gate, init mode
│       ├── build_prompt.py  ← System prompt compiler (identity → memory → skills)
│       ├── backends.py      ← Inference backend abstraction (Ollama, OpenAI-compatible)
│       └── vault_io.py      ← Vault file I/O layer
├── init/                    ← Init prompt templates
├── layouts/                 ← Cockpit layout presets
└── profile/                 ← Profile schemas and templates
```

---

## ADRs

Framework ADRs: `spec/adrs/` — naming `lmf-adr-NNN-short-title.md`.

Instance-level ADRs live in the operator's vault `Decisions/` directory — not in this repo. When writing new LMF ADRs: write `spec/adrs/` version here; the operator mirrors to their vault.

---

## Testing

```bash
# Orchestrator + prompt compiler
cd stack && pytest tests/ -v

# Feature Manager
cd features/feature_manager && pytest tests/ -v
```

All PRs must pass both suites before merge.

---

## Branch and PR Conventions

- No commits to main directly — always a feature branch
- Squash merge only
- PR description must state which Covenant terms the change touches (or "no Covenant impact")
- ADRs for structural decisions before implementation, not after
