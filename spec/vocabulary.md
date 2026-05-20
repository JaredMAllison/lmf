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
