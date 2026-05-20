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
