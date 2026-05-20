# LMF Vocabulary and Summons Frame — Design Spec

**Date:** 2026-05-20
**Status:** Approved
**Produces:** `spec/vocabulary.md`, `spec/frames/summons.md`, `spec/frames/` directory

---

## Context

LMF is growing toward multi-operator deployment: Tori onboarding Scribner, parallel vaults (RPG, data, project, let's play), and eventually community contribution via the Feature Manager. Each of these requires that new operators — technical and non-technical alike — can understand what the system is and how it relates to them, without Jared present to translate.

Currently, component names are scattered across the Covenant, ADRs, the feature inventory, the architecture doc, and the seed schema. Some terms are precise (`operator`, `vault`). Others are implicit (`model`, `binding`, `personality`). Some don't exist yet (`frame`, `deployer` as distinct from `operator`). There is no single authoritative reference.

This spec produces that reference, plus the first metaphor frame — the summons frame — as a complete translation layer over the vocabulary.

---

## Architecture

Two documents, explicit one-way dependency:

```
spec/vocabulary.md          ← stable parent; no knowledge of frames
spec/frames/summons.md      ← child; imports vocabulary, provides translation
spec/frames/office.md       ← stub (future)
spec/frames/familiar.md     ← stub (future)
```

Frames reference vocabulary. Vocabulary never references frames. Adding a new frame is a new file — vocabulary is never modified.

---

## Document 1: `spec/vocabulary.md`

### Purpose

Canonical agnostic reference for every named component in LMF. Operator-agnostic, model-agnostic, metaphor-agnostic. Sits beside the Covenant as a sibling — not a replacement, an extension.

### Structure

**Preamble** — why this exists; relationship to Covenant; how frames use it.

**People**

| Term | Definition | Not |
|---|---|---|
| `operator` | The person the instance is built for and serves. Owns the vault, declares mode, controls the system. | A user. Not a customer. Not a client. |
| `deployer` | The person who sets up the instance. May be the operator themselves, or a trusted person bootstrapping it on their behalf (e.g. Jared setting up Tori's Scribner instance). | Always the operator. The deployer may step back once init completes. |

**The System**

| Term | Definition | Not |
|---|---|---|
| `vault` | The persistent flat-file knowledge base. The operator's second mind. Owned entirely by the operator, stored locally. | A database. Not a cloud service. Not managed by anyone other than the operator. |
| `instance` | A deployed LMF system configured for a specific operator. Each instance has a vault, a personality, a named assistant, and a set of features. Marlin is an instance. Scribner is an instance. | LMF itself. LMF is the architecture; instances are expressions of it. |
| `cockpit` | The unified frontend where panels live. The operator's primary interface to the running system. | A dashboard. Not a portal. Not an app in the conventional sense — the cockpit is the floor. |
| `profile` | The structured cognitive self-model (`LOCAL_MIND_FOUNDATION.md`). Machine-readable frontmatter describing the operator's neurology, needs, and active features. The system draws from this continuously. | A settings file. Not a configuration form. The profile grows through conversation and review. |

**The AI Layer**

| Term | Definition | Not |
|---|---|---|
| `model` | The raw inference backend — the LLM before any vault binding. Claude, Groq, Ollama, OpenCode. Unknown internal mechanics. Stochastic. Capable of unexpected behavior. | The assistant. The model becomes an assistant only after binding. |
| `binding` | The act of connecting a model to a vault and personality to produce an assistant. Init performs the first binding. The binding defines the assistant's behavioral contract for this instance. | Configuration. Binding is a relationship, not a settings file. |
| `personality` | The operator-defined behavioral contract that shapes how the model responds within this instance. Drawn from the profile, the vault context, skills, and memory. What makes this assistant distinct from a blank model. | A persona. Not a costume. Personality is the accumulated contract, not a style setting. |
| `assistant` | The model after binding — the named AI collaborator for a specific instance. `<Name> von <Instance>` (e.g. Ariel von Marlin). Has a personality, can invoke skills, operates within write gate constraints. | A chatbot. Not a product. The assistant is a relationship. |
| `domain expert` | A sub-assistant with a narrower personality scoped to a specific domain (scheduling, coaching, writing). Same model class as the assistant; different imprinting. Invoked by the orchestrator when the operator's intent matches the domain. | A plugin. Not a separate AI. A domain expert is a constrained expression of the same underlying model. |

**Features**

| Term | Definition | Not |
|---|---|---|
| `skill` | A named behavioral pattern the assistant can invoke. Defined in plain language; executable by any model that can follow instructions. | Code. Not a function call. Skills are readable by the operator, not just the runtime. |
| `panel` | A cockpit UI component serving a specific cognitive function. Declares its valid sizes, trust tier, and stability tier. | A widget. A panel has semantic meaning — it fills a specific cognitive gap declared in its identity fields. |
| `init` | The first-time setup and operator onboarding process for an instance. Conversational by design. Produces the profile, establishes the binding, introduces the assistant. Consent-first; never mandatory. | Installation. Init is a relationship-forming process, not a configuration wizard. |
| `write gate` | The permission layer controlling what the assistant can modify in the vault and system. Prevents a model from writing to the operator's exobrain without explicit consent or prior authorization. | A safety feature. The write gate is the contract boundary — what the assistant is authorized to touch. |
| `mode` | Operator-declared context state (`available`, `transit`, `deep-work`, etc.). Declared by the operator, never inferred by the system. Shapes which tasks surface and how the assistant responds. | Status. Mode is a declaration, not a signal the system reads from behavior. |
| `surface` | The act of presenting one task or item to the operator at the right moment. The surfacing engine determines what surfaces and when, based on mode, context, and priority. One at a time. | Notification. Surfacing is considered — one item, chosen by the system, at the right moment. |

**Community**

| Term | Definition | Not |
|---|---|---|
| `trust tier` | Community adoption weight for a feature. Solo (author only) → Vouched (≥2 operators, ≥1 review) → Validated (≥3 operators, ≥2 reviews). Tracks real-world deployment, not theoretical quality. | A rating. Trust tiers are evidence-based, not opinion-based. |
| `stability tier` | Technical maturity of a feature. Experimental → Tested → Stable. Profile-specific: a feature may be Stable for one neurological profile and Experimental for another. | A version number. Stability tracks behavioral fitness across profiles, not code quality alone. |
| `frame` | A metaphor set that translates agnostic vocabulary into culturally familiar terms. Operators choose a frame that fits their existing mental model. The frame is a lens — the vocabulary underneath is unchanged. | The vocabulary itself. A frame is one reading of the system; the vocabulary is what the system actually is. |

---

## Document 2: `spec/frames/summons.md`

### Purpose

The summons frame translates LMF vocabulary into terms drawn from RPG and fantasy literature. Intended for operators with gaming or speculative fiction background. Requires that cultural context — without it, the frame is noise, not signal.

This is the reference frame: the one that shaped the LMF design philosophy most directly. Other frames are translations of the same vocabulary; this one influenced the vocabulary's shape.

### Structure

**Preamble**
- Who this frame is for (RPG/fantasy-literate operators)
- What it captures that other frames don't: the unknown-origin danger register — "powerful creatures of unknown origin, experiment at your peril"
- What it does not capture: the precise contractual nature of binding (the office frame handles this better)

**Translation Table**

| Vocabulary term | Summons term |
|---|---|
| `model` | raw summon |
| `binding` | binding ritual |
| `assistant` | bound summon |
| unbound model (pre-init) | blank summon |
| `personality` | imprinting |
| `vault` | grimoire |
| `profile` | the operator's sigil |
| `init` | the summoning ritual |
| `operator` | summoner |
| `deployer` | first summoner |
| `domain expert` | specialized summon |
| `skill` | invocation |
| `cockpit` | summoning chamber |
| `write gate` | binding contract |
| `mode` | the summoner's declared state |
| `trust tier` | vouching record |
| `stability tier` | field record |
| `frame` | lens |
| `instance` | bound circle |

**The Philosophy**
Three things the summons frame does that clinical language cannot:
1. Names the danger correctly — you do not know how a model works internally. It is not a calculator. It is stochastic, capable of unexpected output, and shaped by training you didn't control. "Experiment at your peril" is honest.
2. Justifies the architecture — the write gate is not paranoia; it is what any sensible summoner does before letting an unknown creature write in their grimoire. Operator-declared mode is not a design quirk; the summoner must declare their state because the summon cannot reliably read it. Trust tiers exist because you want to know how many summoners have worked with this creature and what happened.
3. Names the relationship — `Ariel von Marlin` is not a product name. It is a bound summon's name. The `von` is a binding word. The instance name says where the creature is contracted to.

**Where It Surfaces**
- Init: the first explanation of what is about to happen, if the operator has RPG/fantasy context
- CONTRIBUTING.md: framing for contributors submitting a new panel or skill ("you are adding a new summon type to the grimoire")
- Domain experts introduction: "you are narrowing a summon's contract to a specific domain"
- Trust tier documentation: "a Solo summon has been worked with by one summoner only"

---

## Relationship to the Systemic Legibility Initiative

This spec is the first deliverable of a broader effort to make LMF legible across operator types:

- **Tori / Scribner onboarding** — Tori is a writer, not a technical operator. The vocabulary gives the deployer (Jared) precise terms; the frame gives Tori a legible entry point.
- **Parallel vaults** — RPG vaults, data vaults, project vaults, let's play vaults all become LMF instances once the vocabulary is precise enough to name what they have in common and where they differ. (Vault type taxonomy is a downstream deliverable from this work.)
- **Feature Manager deployment** — the vocabulary makes install manifests legible: a `domain expert` manifest is distinct from a `skill` manifest is distinct from a `panel` manifest because those terms now have precise definitions.
- **Community contribution** — the CONTRIBUTING.md becomes coherent once the vocabulary is stable. Contributors know what they're contributing.

---

## Out of Scope

- The metaphor selector feature (which frame to offer which operator) — downstream
- Other frame documents (office, familiar, ghost) — stubs only; full frames are future work
- Vault type taxonomy (what distinguishes a personal vault from a project vault from a reference vault) — feeds from this work but is its own spec
- Music panel / ambient cockpit engagement — separate feature
- Vault type taxonomy (naming distinction between personal exobrain vaults, publicly-derived knowledge vaults, and project vaults) — this question surfaced during design; it is downstream vocabulary work that depends on `spec/vocabulary.md` being stable first
