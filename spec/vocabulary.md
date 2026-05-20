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
