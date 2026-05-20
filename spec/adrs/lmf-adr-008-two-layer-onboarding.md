---
title: "LMF-ADR-008: Two-Layer Onboarding Model"
type: adr
project: Local Mind Foundation
status: accepted
date: 2026-04-20
tags: [adr, lmf, onboarding, init, architecture]
parent_adr: lmf-adr-001-local-mind-foundation-architecture
---

## Context

The init script (ADR-001) bootstraps a new LMF instance through conversation. But a fully blank-slate interview cannot work: the questions a child should be asked are different from those an adult configures for themselves, which are different again from a work brain setup. If the interview has no prior context, it either asks too much (overwhelming) or assumes wrong things (broken experience).

The deployer and the end operator are not always the same person. A parent deploys Jaina's instance. An IT administrator deploys a work brain. Jared deploys his own. Each deployer has different information and different responsibilities. The end operator — whoever sits down for the interview — should only see what is relevant to them.

## Decision

Onboarding has two distinct layers with two distinct audiences.

---

### Layer 1 — Pre-configuration (`deploy.yaml`)

Set by the **deployer** before the first run. The deployer may or may not be the end operator.

```yaml
instance_name: Jaina          # names the vault; used in "von <instance_name>"
trust_profile: child          # personal | work | child | household
operator_age_group: child     # child | adult (shapes interview register and question set)
language: en                  # ISO 639-1; future: locale for date/time formats
available_features: [tasks, projects, daily, inbox, creative]
assistant_name: ""            # optional: pre-assign; if blank, operator names the assistant in interview
deployer_email: ""            # required for work and child profiles (employer / parent contact)
```

`deploy.yaml` is read once at first run. It is not the cognitive profile — it is the context that shapes the interview that produces the profile.

**For child and work profiles:** `deploy.yaml` is the deployer's responsibility. The end operator never sees it. For personal profiles, the operator fills it in themselves (or accepts defaults).

---

### Layer 2 — The Interview

Conducted by the **end operator** on first run. The assistant reads `deploy.yaml`, selects the appropriate question set and register, and begins the conversation.

The interview is not a form. It is a conversation that ends when the assistant has enough information to:
1. Write `LOCAL_MIND_FOUNDATION.md` (the cognitive profile)
2. Seed the vault with appropriate structure
3. Activate the features listed in `available_features`
4. Introduce itself by name

**Question set is profile-driven:**

| Profile | Interview focus |
|---|---|
| Personal | What do you want help with? What do you drop? What does a good day look like? |
| Work | What is your role? What tools does your employer use? What data stays work-only? |
| Child | What are you working on? What do you want to remember? What should your assistant call you? |
| Household | Who lives here? What shared things need tracking? Who is the primary contact? |

**Register is age-group-driven:**
- `child`: simpler language, shorter questions, more confirmation, no jargon
- `adult`: normal register, assumes basic self-awareness

---

### What Pre-config Does Not Include

- The cognitive profile (that comes from the interview)
- Skill content or vault note content (seeded by the init script post-interview)
- The assistant's personality (emerges from the identity document, not deploy config)

---

## Consequences

**Enables:**
- A parent can configure Jaina's instance without Jaina being present — then hand it to her for the interview
- The interview is always appropriately scoped — a child doesn't get asked about work data sovereignty
- Deployers with technical context (IT, parents) handle the structural decisions; end operators handle the personal ones
- `deploy.yaml` is simple enough for a non-technical parent to fill out

**Forecloses:**
- Fully self-configuring blank-slate instances — some pre-configuration is always required (even if it's just accepting defaults for a personal instance)
- The interview adapting to profile mid-conversation — trust profile is fixed at deploy time, not discovered through the interview

**Trade-offs:**
- Two-step process adds friction for solo personal deployments — mitigated by sensible defaults that require minimal editing
- `deploy.yaml` must be well-documented; a confused deployer produces a broken interview
