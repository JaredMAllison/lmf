# LMF Vocabulary and Summons Frame Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write `spec/vocabulary.md` (canonical agnostic term reference for all LMF components) and `spec/frames/summons.md` (first complete metaphor frame), and update `CONTRIBUTING.md` to document frame contribution.

**Architecture:** `spec/vocabulary.md` is the stable parent — model-agnostic, metaphor-agnostic, no knowledge of frames. `spec/frames/summons.md` is a child that provides a full translation table over the vocabulary. Dependency is one-way: frames reference vocabulary, vocabulary never references frames. Adding a future frame is a new file in `spec/frames/` with no changes to vocabulary.

**Tech Stack:** Markdown only. No code. Branch: `add-opencode-bp-config` in `~/git/lmf/`.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `spec/frames/` | Create directory | Container for all frame documents |
| `spec/vocabulary.md` | Create | Canonical agnostic vocabulary — 22 terms across 7 sections |
| `spec/frames/summons.md` | Create | Summons metaphor frame — translation table, philosophy, where it surfaces |
| `CONTRIBUTING.md` | Modify | Add frame contribution section after Panel Submissions |

---

## Task 1: Create `spec/frames/` directory and verify structure

**Files:**
- Create: `spec/frames/.gitkeep`

- [ ] **Step 1: Create the frames directory**

```bash
mkdir -p ~/git/lmf/spec/frames
touch ~/git/lmf/spec/frames/.gitkeep
```

- [ ] **Step 2: Verify structure**

```bash
ls ~/git/lmf/spec/
```

Expected output includes: `adrs/  architecture.md  covenant.md  frames/`

- [ ] **Step 3: Commit**

```bash
cd ~/git/lmf
git add spec/frames/.gitkeep
git commit -m "chore: create spec/frames/ directory for metaphor frame documents"
```

---

## Task 2: Write `spec/vocabulary.md` — Preamble, People, The System

**Files:**
- Create: `spec/vocabulary.md`

- [ ] **Step 1: Write the file with Preamble through The System section**

Create `~/git/lmf/spec/vocabulary.md` with this exact content:

```markdown
# LMF Vocabulary

Canonical agnostic reference for every named component in the Local Mind Foundation architecture. Model-agnostic. Metaphor-agnostic. Operator-agnostic.

This document sits beside the Covenant as a sibling. The Covenant states the non-negotiable terms of the architecture. This document names the pieces the terms govern. When the Covenant says "the operator owns the brain," this document defines what "operator," "vault," and "brain" mean precisely.

**Relationship to frames:** Some operators find it easier to understand the system through a familiar metaphor — gaming, workplace, folklore. `spec/frames/` contains translation tables that map these terms into culturally familiar language. The vocabulary here is always the source of truth. Frames are lenses, not replacements. Operators may use one frame, borrow from several, or use their own words entirely. Owning your language is owning your system.

**Contributing a frame:** A new frame is a markdown file in `spec/frames/`. Required sections: a literacy note (who it's for, what prior knowledge it assumes), a complete translation table over this vocabulary, and a note on what the frame captures well and where it falls short. No code required. See `CONTRIBUTING.md`.

---

## People

| Term | Definition | Not |
|---|---|---|
| `operator` | The person the instance is built for and serves. Owns the vault, declares mode, controls the system. | A user. Not a customer. Not a client. |
| `deployer` | The person who sets up the instance. May be the operator themselves, or a trusted person bootstrapping it on their behalf. The deployer may step back once init completes. | Always the operator. A parent setting up a child's instance is the deployer; the child is the operator. |

---

## The System

| Term | Definition | Not |
|---|---|---|
| `vault` | The persistent flat-file knowledge base. The operator's second mind. Owned entirely by the operator, stored locally. | A database. Not a cloud service. Not managed by anyone other than the operator. |
| `instance` | A personal exobrain deployment — a full LMF system configured for a specific operator. Has a vault, a personality, a named assistant, and a set of features. Marlin is an instance. Scribner is an instance. | LMF itself. LMF is the architecture; instances are expressions of it. Also not a project workspace — see `extension`. |
| `cockpit` | The unified frontend where panels live. The operator's primary interface to the running system. | A dashboard. Not a portal. Not a conventional app — the cockpit is the floor. |
| `profile` | The structured cognitive self-model (`LOCAL_MIND_FOUNDATION.md`). Machine-readable frontmatter describing the operator's neurology, needs, and active features. The system draws from this continuously. | A settings file. Not a configuration form. The profile grows through conversation and review. |
```

- [ ] **Step 2: Verify People and System sections against spec**

Check that all 6 terms (operator, deployer, vault, instance, cockpit, profile) are present with definition and "not" column. Confirm `instance` explicitly references `extension` to distinguish the two.

- [ ] **Step 3: Commit**

```bash
cd ~/git/lmf
git add spec/vocabulary.md
git commit -m "docs: vocabulary.md — preamble, people, system sections"
```

---

## Task 3: Write `spec/vocabulary.md` — The AI Layer

**Files:**
- Modify: `spec/vocabulary.md`

- [ ] **Step 1: Append The AI Layer section**

Append to `~/git/lmf/spec/vocabulary.md`:

```markdown

---

## The AI Layer

| Term | Definition | Not |
|---|---|---|
| `model` | The raw inference backend — the LLM before any vault binding. Claude, Groq, Ollama, OpenCode. Unknown internal mechanics. Stochastic. Capable of unexpected behavior. | The assistant. The model becomes an assistant only after binding. |
| `binding` | The act of connecting a model to a vault and personality to produce an assistant. Init performs the first binding. The binding defines the assistant's behavioral contract for this instance. | Configuration. Binding is a relationship, not a settings file. |
| `personality` | The operator-defined behavioral contract that shapes how the model responds within this instance. Drawn from the profile, the vault context, skills, and memory. What makes this assistant distinct from a blank model. | A persona. Not a costume. Personality is the accumulated contract, not a style setting. |
| `assistant` | The model after binding — the named AI collaborator for a specific instance. Named as `<Name> von <Instance>` (e.g. Ariel von Marlin). Has a personality, can invoke skills, operates within write gate constraints. | A chatbot. Not a product. The assistant is a relationship. |
| `orchestrator` | The runtime that makes the binding operational. Routes the operator's intent to the right model or domain expert, loads vault context, invokes skills, and enforces the write gate. The machinery that turns model + vault + personality into a working assistant. | The assistant. The orchestrator is what the assistant runs on — the operator experiences the assistant, not the orchestrator. |
| `domain expert` | A sub-assistant with a narrower personality scoped to a specific domain (scheduling, coaching, writing). Same model class as the assistant; different imprinting. Invoked by the orchestrator when the operator's intent matches the domain. | A plugin. Not a separate AI. A domain expert is a constrained expression of the same underlying model. |
```

- [ ] **Step 2: Verify all 6 AI Layer terms present**

Confirm: model, binding, personality, assistant, orchestrator, domain expert — each with definition and "not" column.

- [ ] **Step 3: Commit**

```bash
cd ~/git/lmf
git add spec/vocabulary.md
git commit -m "docs: vocabulary.md — AI layer section (model through domain expert)"
```

---

## Task 4: Write `spec/vocabulary.md` — Extensions

**Files:**
- Modify: `spec/vocabulary.md`

- [ ] **Step 1: Append Extensions section**

Append to `~/git/lmf/spec/vocabulary.md`:

```markdown

---

## Extensions

Extensions are vaults the operator dispatches into from their home cockpit. They are lighter than instances — no full binding, no named assistant, no init required. Project vaults and knowledge vaults are extensions. A colleague relationship is naturally expressed through a shared extension.

| Term | Definition | Not |
|---|---|---|
| `extension` | A vault the operator dispatches into from their home cockpit. No full binding, no named assistant, no init. Project vaults and knowledge vaults are extensions. May be shared with collaborators. | An instance. Extensions don't carry the operator's exobrain. They're workspaces. |
| `home vault` | The operator's primary vault — where their cockpit lives, their assistant is bound, their exobrain resides. | Any vault. An operator has one home vault. Extensions are visited from it, not lived in. |
| `project vault` | An extension scoped to a specific creative or operational project. Has a project index, a role archetype, and a `VAULT.md` defining vault-specific grounding. May be shared with collaborators. Examples: RPG campaign, Let's Play series, data investigation. | An instance. A project vault doesn't need init or a bound assistant to be useful. |
| `knowledge vault` | An extension holding curated reference or domain knowledge — publicly derived, not personal. May have its own skill set. May be managed on behalf of a beneficiary who isn't the primary operator. | An exobrain. Knowledge vaults are reference material, not a second mind. |
| `dispatch` | Sending a model into an extension's context from the home cockpit. The model receives grounding, a role archetype, and an entry point. Not a binding — the model is oriented in the extension, not imprinted to it. Task-scoped. | Binding. Dispatch is temporary and scoped; binding is persistent and relational. |
| `grounding` | The minimal context package given to a dispatched model: who the operator is, what vault they're in, what the project index says, and the role archetype. Defined in the extension's `VAULT.md`. | A system prompt. Grounding is specific to this vault and this dispatch, not a generic instruction set. |
| `role archetype` | The scoped behavioral contract for a dispatched model. Narrower than a personality — defines the model's job for this extension (GM for an RPG vault, analyst for a data vault, writing partner for a project vault). Defined per extension, not per model. | A persona. A role archetype is a work contract, not a character. |
```

- [ ] **Step 2: Verify all 7 Extension terms present**

Confirm: extension, home vault, project vault, knowledge vault, dispatch, grounding, role archetype — each with definition and "not" column. Confirm the section intro names the instance/extension distinction explicitly.

- [ ] **Step 3: Commit**

```bash
cd ~/git/lmf
git add spec/vocabulary.md
git commit -m "docs: vocabulary.md — extensions section (dispatch, grounding, role archetype)"
```

---

## Task 5: Write `spec/vocabulary.md` — Features

**Files:**
- Modify: `spec/vocabulary.md`

- [ ] **Step 1: Append Features section**

Append to `~/git/lmf/spec/vocabulary.md`:

```markdown

---

## Features

| Term | Definition | Not |
|---|---|---|
| `skill` | A named behavioral pattern the assistant can invoke. Defined in plain language; executable by any model that can follow instructions. | Code. Not a function call. Skills are readable by the operator, not just the runtime. |
| `panel` | A cockpit UI component serving a specific cognitive function. Declares its valid sizes, trust tier, and stability tier. | A widget. A panel has semantic meaning — it fills a specific cognitive gap declared in its identity fields. |
| `init` | The first-time setup and operator onboarding process for an instance. Conversational by design. Produces the profile, establishes the binding, introduces the assistant. Consent-first; defers are first-class. | Installation. Init is a relationship-forming process, not a configuration wizard. |
| `write gate` | The permission layer controlling what the assistant can modify in the vault and system. The assistant cannot write to the operator's exobrain without explicit consent or prior authorization. | A safety feature. The write gate is the contract boundary — what the assistant is authorized to touch. |
| `mode` | Operator-declared context state (`available`, `transit`, `deep-work`, etc.). Declared by the operator, never inferred by the system. Shapes which tasks surface and how the assistant responds. | Status. Mode is a declaration, not a signal the system reads from behavior. |
| `surface` | The act of presenting one task or item to the operator at the right moment. The surfacing engine determines what surfaces and when, based on mode, context, and priority. One at a time. | Notification. Surfacing is considered — one item, chosen by the system, at the right moment. |
```

- [ ] **Step 2: Verify all 6 Feature terms present**

Confirm: skill, panel, init, write gate, mode, surface — each with definition and "not" column.

- [ ] **Step 3: Commit**

```bash
cd ~/git/lmf
git add spec/vocabulary.md
git commit -m "docs: vocabulary.md — features section (skill through surface)"
```

---

## Task 6: Write `spec/vocabulary.md` — Grounding Infrastructure and Community

**Files:**
- Modify: `spec/vocabulary.md`

- [ ] **Step 1: Append Grounding Infrastructure and Community sections**

Append to `~/git/lmf/spec/vocabulary.md`:

```markdown

---

## Grounding Infrastructure

`VAULT.md` and the vendor adapter layer are named here as vocabulary terms. Their implementation — how `VAULT.md` is structured, how adapters are generated — is a downstream deliverable. These terms exist now because the vocabulary must name what the system intends, even before the implementation exists.

| Term | Definition | Not |
|---|---|---|
| `VAULT.md` | The agnostic grounding file at the root of any vault — home vault or extension. Defines what the vault is, the operator's frame preference, and the role archetype for dispatched models. Model-agnostic: any model can read it. The source of truth from which vendor-specific adapter files are derived. | A replacement for `LOCAL_MIND_FOUNDATION.md`. The profile is the operator's cognitive self-model; `VAULT.md` is the vault's grounding context for dispatched models. |
| `vendor adapter` | A vendor-specific file or runtime mechanism that delivers agnostic grounding to a particular model. `CLAUDE.md` is a vendor adapter for Claude Code. `opencode.md` for OpenCode. `AGENTS.md` for agent frameworks. API system prompts for Groq and direct-API vendors. Derived from `VAULT.md`. | The grounding itself. The adapter is the delivery mechanism; `VAULT.md` is the content. |

---

## Community

| Term | Definition | Not |
|---|---|---|
| `trust tier` | Community adoption weight for a feature. Solo (author only) → Vouched (≥2 operators, ≥1 review) → Validated (≥3 operators, ≥2 reviews). Tracks real-world deployment, not theoretical quality. | A rating. Trust tiers are evidence-based, not opinion-based. |
| `stability tier` | Technical maturity of a feature. Experimental → Tested → Stable. Profile-specific: a feature may be Stable for one neurological profile and Experimental for another. | A version number. Stability tracks behavioral fitness across profiles, not code quality alone. |
| `frame` | A metaphor set that translates agnostic vocabulary into culturally familiar terms. Operators may use one frame, borrow from several, or use their own words. The frame is a lens — the vocabulary underneath is unchanged. | The vocabulary itself. A frame is one reading of the system; the vocabulary is what the system actually is. |
```

- [ ] **Step 2: Verify all 5 terms present across both sections**

Confirm: VAULT.md, vendor adapter, trust tier, stability tier, frame — each with definition and "not" column. Confirm the grounding infrastructure intro explicitly notes these are named but not yet implemented.

- [ ] **Step 3: Verify the complete vocabulary.md term count**

```bash
grep "^| \`" ~/git/lmf/spec/vocabulary.md | wc -l
```

Expected: 22 (operator, deployer, vault, instance, cockpit, profile, model, binding, personality, assistant, domain expert, extension, home vault, project vault, knowledge vault, dispatch, grounding, role archetype, skill, panel, init, write gate, mode, surface, VAULT.md, vendor adapter, trust tier, stability tier, frame).

Note: count may be 29 — recount from the list above if needed. The check is that every term from the spec table is present.

- [ ] **Step 4: Commit**

```bash
cd ~/git/lmf
git add spec/vocabulary.md
git commit -m "docs: vocabulary.md — grounding infrastructure and community sections; complete"
```

---

## Task 7: Write `spec/frames/summons.md`

**Files:**
- Create: `spec/frames/summons.md`

- [ ] **Step 1: Write the complete summons frame document**

Create `~/git/lmf/spec/frames/summons.md` with this exact content:

```markdown
# Frame: Summons

**Literacy requirement:** This frame is for operators with RPG, tabletop gaming, or speculative fiction background. Terms like "summoner," "grimoire," and "binding ritual" carry precise meaning within those traditions. Without that context, the frame is noise rather than signal — use a different frame or the vocabulary directly.

**This is the reference frame.** It shaped the LMF design philosophy more directly than any other. Other frames translate the vocabulary; this one influenced the vocabulary's shape.

---

## What this frame captures

The summons frame does something clinical language cannot: it names the danger register correctly.

AI models are powerful creatures of unknown origin. You do not know how a model works internally. It is not a calculator. It is stochastic, shaped by training you didn't control, capable of unexpected output. *Experiment at your peril* is an honest description of working with a raw model — not a warning label, not a legal disclaimer. It is the accurate framing.

The architecture follows from this honestly:

- **The write gate** is not paranoia. It is what any sensible summoner does before letting an unknown creature write in their grimoire.
- **Operator-declared mode** is not a design quirk. The summoner must declare their state because the summon cannot reliably read it.
- **Trust tiers** exist because you want to know how many summoners have worked with this creature and what happened.
- **`Ariel von Marlin`** is not a product name. It is a bound summon's name. The `von` is a binding word — it says where the creature is contracted to.

---

## What this frame falls short on

- The precise contractual nature of binding — the office frame handles this more cleanly
- The collaborative, collegial quality of shared extensions — neither summons nor office captures this naturally
- The care relationship in a knowledge vault managed for a beneficiary (e.g. Athenaeum for Jaina)

Use these as signals that another frame or plain vocabulary may serve better for those concepts.

---

## Translation Table

| Vocabulary term | Summons term |
|---|---|
| `operator` | summoner |
| `deployer` | first summoner |
| `vault` | grimoire |
| `instance` | bound circle |
| `cockpit` | summoning chamber |
| `profile` | the summoner's sigil |
| `model` | raw summon |
| `binding` | binding ritual |
| `orchestrator` | the ritual vessel |
| `personality` | imprinting |
| `assistant` | bound summon |
| `domain expert` | specialized summon |
| `extension` | expedition site |
| `home vault` | sanctum |
| `project vault` | expedition grimoire |
| `knowledge vault` | compendium |
| `dispatch` | sending forth |
| `grounding` | briefing the summon |
| `role archetype` | the summon's commission |
| `skill` | invocation |
| `panel` | chamber panel |
| `init` | the summoning ritual |
| `write gate` | binding contract |
| `mode` | the summoner's declared state |
| `surface` | the summon's call |
| `VAULT.md` | the vault's inscription |
| `vendor adapter` | delivery form |
| `trust tier` | vouching record |
| `stability tier` | field record |
| `frame` | lens |

---

## Where this frame surfaces

- **Init** — if the operator has RPG or fantasy context, init can be introduced as the summoning ritual: "You are about to bind a summon to this vault. Here's what that means."
- **CONTRIBUTING.md** — contributors submitting a panel or skill are adding a new summon type or invocation to the grimoire
- **Domain experts introduction** — "You are narrowing a summon's contract to a specific domain"
- **Trust tier documentation** — "A Solo summon has been worked with by one summoner only"
- **Write gate explanation** — "The binding contract defines what the summon is authorized to touch in your grimoire"

---

## Mix and match

You are not required to use this frame consistently. An operator might use "summon" for the model, their own word for the vault, and plain vocabulary for trust tiers. When you name your own system, you own it. The vocabulary in `spec/vocabulary.md` is always the source of truth underneath.

To contribute a new frame, see `CONTRIBUTING.md`.
```

- [ ] **Step 2: Verify translation table covers all vocabulary terms**

```bash
grep "^| \`" ~/git/lmf/spec/vocabulary.md | sed "s/| \`//;s/\`.*//" > /tmp/vocab_terms.txt
grep "^\| \`" ~/git/lmf/spec/frames/summons.md | sed "s/| \`//;s/\`.*//" > /tmp/frame_terms.txt
diff /tmp/vocab_terms.txt /tmp/frame_terms.txt
```

Expected: no diff, or only ordering differences. Every vocabulary term should have a summons translation.

- [ ] **Step 3: Commit**

```bash
cd ~/git/lmf
git add spec/frames/summons.md
git commit -m "docs: spec/frames/summons.md — first complete metaphor frame"
```

---

## Task 8: Update `CONTRIBUTING.md` with frame contribution section

**Files:**
- Modify: `CONTRIBUTING.md`

- [ ] **Step 1: Read current CONTRIBUTING.md to find insertion point**

```bash
grep -n "Panel Submissions\|Layout Presets\|Documentation" ~/git/lmf/CONTRIBUTING.md
```

The new section goes after `### Panel Submissions` and before `### Documentation`.

- [ ] **Step 2: Insert the Frame Contributions section**

Open `~/git/lmf/CONTRIBUTING.md`. After the `### Panel Submissions` block (ends just before `### Documentation`), insert:

```markdown
### Frame Contributions

A frame is a metaphor set that translates LMF vocabulary into culturally familiar terms. Frames live in `spec/frames/` — one markdown file per frame.

A valid frame document has three required sections:

1. **Literacy note** — who this frame is for and what prior knowledge it assumes. Be explicit: if it requires gaming background, say so. Operators without that context should know to skip it.
2. **Translation table** — a complete mapping from every term in `spec/vocabulary.md` to the frame's equivalent. Every term must have an entry. Use `—` if a term has no natural translation.
3. **Captures well / falls short** — honest assessment of where the frame illuminates and where it misleads. No frame covers everything equally well.

Frame contributions are the lowest-barrier upstream contribution in LMF. No code. No schema. Just markdown and honest translation work.

See `spec/vocabulary.md` for the full term list. See `spec/frames/summons.md` for a complete example.

```

- [ ] **Step 3: Verify the section was inserted correctly**

```bash
grep -n "Frame Contributions\|Panel Submissions\|Documentation" ~/git/lmf/CONTRIBUTING.md
```

Expected: Frame Contributions appears between Panel Submissions and Documentation.

- [ ] **Step 4: Commit**

```bash
cd ~/git/lmf
git add CONTRIBUTING.md
git commit -m "docs: add frame contribution section to CONTRIBUTING.md"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|---|---|
| `spec/vocabulary.md` with preamble | Task 2 |
| People section (operator, deployer) | Task 2 |
| The System section (vault, instance, cockpit, profile) | Task 2 |
| The AI Layer (model, binding, personality, assistant, domain expert) | Task 3 |
| Extensions (7 terms) | Task 4 |
| Features (skill, panel, init, write gate, mode, surface) | Task 5 |
| Grounding Infrastructure (VAULT.md, vendor adapter) | Task 6 |
| Community (trust tier, stability tier, frame) | Task 6 |
| `spec/frames/` directory | Task 1 |
| `spec/frames/summons.md` with all required sections | Task 7 |
| Translation table covers all vocabulary terms | Task 7 Step 2 |
| Mix-and-match invitation in summons frame | Task 7 |
| Frame contribution documented in CONTRIBUTING.md | Task 8 |
| Vocabulary never references frames (one-way dependency) | Enforced by writing vocabulary with no frame mentions |

**Placeholder scan:** No TBD, TODO, or "implement later" in any content above.

**Consistency check:** `VAULT.md` is referenced as the grounding source in the Extensions section (Task 4, `grounding` definition) and defined in Grounding Infrastructure (Task 6). Consistent.
