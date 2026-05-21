# Spec: Ariel Vault Agent Persona

## Overview
Create a vault‑agent persona for Ariel that operates within the Marlin vault. The persona must:
- Harden against prompt injection by sanitizing and validating all incoming prompts.
- Manage context‑window budgeting: track token usage, truncate or summarize older context, and prioritize recent relevant information.
- Integrate with the spec‑kit workflow so that the persona can be generated, tested, and iterated via `speckit` commands.

## Requirements
1. **Thinking to Yourself (Internal Monologue)**
   - Ariel must perform an internal "thinking" pass before formulating a response.
   - Purpose: Identify which specific vault documents or skills are required for the current turn.
   - Truncation Strategy: Only "read" and include the specific content identified in the thinking step, rather than loading broad directories.
2. **On-Demand Context Loading**
   - Base personality is trimmed to a "Vault Literacy" core (knowing *how* to find info).
   - Use a `read_vault_doc` tool to fetch specific notes/ADRs identified during the "thinking" pass.
3. **Session Context Awareness**
   - Ariel reads a cooperatively populated Session Topic YAML (`.session/current_topic.yaml`) at startup to understand the session's framing.
   - Ariel may propose updates to this YAML (e.g., appending insights) for user approval, treating it as trusted internal state.
4. **Hardware-Aware Design**
   - Optimization for RTX 3070 (8GB VRAM).
   - Prefer 4-bit/8-bit quantization for local inference (Ollama/Llama.cpp).
   - Context window management must prioritize low VRAM overhead.
5. **Prompt‑Injection Hardening**
   - Strip or escape special characters that could alter system prompts.
   - **Sanitization Strategy**: Wrap untrusted input in delimiters. If a forbidden directive (e.g., `!exec`, `!shutdown`) is detected, proceed with the request but append a "Potential Injection Detected" warning flag to the agent's response.
   - Log any detected injection attempts to `Logs/prompt_injection.log`.
6. **Context‑Window Budgeting**
   - Maintain a rolling token count for the conversation.
   - **Threshold**: 8,192 tokens (prioritizing "personal connection" and working memory over raw speed).
   - When the token budget is exceeded, automatically extract "Key Insights" (decisions, logic, associations) using an internal prompt.
   - Store insights as a Marlin Insight note in `Vault/ContextSummaries/` via the gated write tool.
   - Prune **50% of the conversation context buffer** (preserving recent raw exchange for continuity).
   - Inject a context link (`[[Insight: Slugified Topic]]`) into the system prompt for the next turn.
7. **Spec‑Kit Integration**
   - Provide a CLI entry point `ariel_vault_agent` that reads the spec and generates the agent code.
   - Include unit tests covering injection detection and budgeting logic.
8. **Observability**
   - Emit structured logs (JSON) for injection events and budgeting actions.
   - Expose a simple status endpoint returning current token usage.

## Success Criteria (Measurable Outcomes)
- [ ] Agent rejects or sanitizes any prompt containing a forbidden directive.
- [ ] Token usage never exceeds 8,192 tokens; older context is summarized.
- [ ] Injection warning appears in UI/output within 100ms of detection.
- [ ] All tests pass (`pytest -q`).

## Clarifications
### Session 2026-05-09
- Q: What is the hard token limit for context budgeting? → A: 8,192 tokens (Option C - Deep).
- Q: How should prompt injection attempts be handled? → A: Sanitize by wrapping in delimiters and append a warning flag to the output (Option A).

## Acceptance Criteria
- [ ] Agent rejects or sanitizes any prompt containing a forbidden directive.
- [ ] Token usage never exceeds the configured budget; older context is summarized.
- [ ] All tests pass (`pytest -q`).
- [ ] Specification is version‑controlled in `.specify/specs/`.
