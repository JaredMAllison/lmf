---
title: "LMF-ADR-010: Input Mode Configuration"
type: adr
project: Local Mind Foundation
status: accepted
date: 2026-04-20
tags: [adr, lmf, input, accessibility, child, onboarding]
parent_adr:
  - lmf-adr-008-two-layer-onboarding
  - lmf-adr-006-instance-trust-profiles
---

## Context

LMF instances may eventually support voice input (speech-to-text). For some operators this removes friction and lowers the activation floor — a core LMF goal. For others, particularly children learning to type, voice input undermines a skill-building goal that the deployer has set intentionally.

These two goals are in direct tension. The system cannot optimize for both simultaneously. The deployer must declare intent.

Reference case: Jaina. Her parent wants her to use the assistant as a tool for learning to type, not a replacement for it. Voice input would be the path of least resistance and would foreclose the skill-building opportunity. At the same time, voice may be appropriate later — as a reward, for quick captures, or when she genuinely needs it.

## Decision

Input mode is a deployer-set configuration in `deploy.yaml`:

```yaml
input_mode: keyboard   # keyboard | voice | both
```

**`keyboard` mode:**
- Text input only. No voice transcription.
- The assistant is patient with slow, incomplete, or typo-filled input.
- The assistant responds to intent, not literal text — it does not silently correct spelling or grammar in its responses, but it understands what was meant.
- Typos are never echoed back corrected. The operator's words are their words.
- This is the default for child profiles.

**`voice` mode:**
- Speech-to-text input. Text output (or text-to-speech if the UI supports it).
- Appropriate for operators with motor difficulties, low typing confidence, or high-bandwidth capture needs.
- Not available in keyboard mode.

**`both` mode:**
- Operator chooses per message. Voice for quick captures; keyboard for sustained work.
- The UI must make switching explicit — not automatic.

---

## Keyboard Mode and Skill Building

When `input_mode: keyboard` is set with `operator_age_group: child`, the assistant applies additional patience behaviors:

- Waits without prompting if the operator goes quiet mid-sentence
- Does not ask "did you mean X?" for minor typos — infers and continues
- Keeps its own responses short so the operator's reading load stays low
- Celebrates completed typing ("got it") without drawing attention to errors

The goal is that the interface never makes typing feel punishing. The cost of trying is zero. The reward is visible and immediate.

---

## Input Mode Is Not Accessibility

Voice input is often framed as an accessibility feature. In LMF it is one option among several, not the default accommodation for any profile. Accessibility is served by the patience behaviors, short turns, and low-friction response style — not by removing the keyboard.

An operator who cannot type at all requires a different configuration conversation with the deployer, not a default voice mode.

---

## Consequences

**Enables:**
- Deployer can explicitly protect a skill-building context from convenience bypass
- Voice and keyboard modes are cleanly separated — no accidental activation
- Input mode can evolve per instance (keyboard now, both later) without architectural change

**Forecloses:**
- The assistant auto-detecting and switching input modes based on operator behavior — mode is deployer-declared, not inferred

**Trade-offs:**
- A child who genuinely cannot keep up with keyboard input has no fallback in `keyboard` mode — the deployer must make this call carefully
- `both` mode requires UI work to make switching explicit; it cannot be a hidden feature
