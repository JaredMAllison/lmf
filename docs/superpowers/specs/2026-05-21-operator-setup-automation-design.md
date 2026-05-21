# LMF Operator Setup Automation — Design

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Take a new LMF operator from zero to a running instance in one shell command, with no assumed prerequisites beyond Ollama installed.

**Architecture:** A thin platform-specific bootstrap script checks prerequisites and clones the repo; a stdlib-only Python wizard handles interactive configuration; the two are decoupled so Fritz-tier operators can skip the bootstrap and run the wizard directly.

**Two tiers:**
- **Jason tier** — pastes a one-liner from the README, answers three prompts, gets a running instance
- **Fritz tier** — `git clone` + `pip install requests pyyaml` + `python scripts/lmf-setup.py`, or edits `config.yaml` directly and skips the wizard entirely

---

## Architecture

```
scripts/setup.ps1        ← Windows bootstrap (PowerShell, no Python required)
scripts/setup.sh         ← Linux/Mac bootstrap (bash, no Python required)
        ↓ (clone repo, pip install, hand off)
scripts/lmf-setup.py     ← interactive wizard (stdlib-only Python)
        ↓ (writes)
stack/operator/config.yaml   ← orchestrator config
<vault_path>/                ← empty vault directory (no VAULT.md = init mode)
```

---

## Components

### `scripts/setup.ps1` (Windows bootstrap)

1. Check `python --version` — if missing: print `https://python.org/downloads`, exit 1
2. Check `git --version` — if missing: print `https://git-scm.com/download/win`, exit 1
3. `git clone https://github.com/JaredMAllison/lmf.git "$HOME\lmf"`
4. `cd "$HOME\lmf"`
5. `pip install requests pyyaml`
6. `python scripts\lmf-setup.py`

### `scripts/setup.sh` (Linux/Mac bootstrap)

Same logic, bash syntax, clones to `~/lmf`.

### `scripts/lmf-setup.py` (interactive wizard)

Stdlib-only — runs before or after `pip install` without breaking. No third-party imports.

**Prompt sequence:**

```
1. Vault path
   Default (Windows): C:\Users\<username>\lmf-vault
   Default (Linux/Mac): ~/lmf-vault
   Operator presses Enter to accept or types a custom path.

2. Assistant name
   "What should your assistant be called?"
   No default — required answer.

3. Model selection
   Run `ollama list` and display numbered results.
   If no models: print "No Ollama models found. Run 'ollama pull qwen2.5:7b' then re-run setup." Exit 1.
   Operator picks by number.
```

**Optional flags:**
- `--dry-run` — prints what would be written without creating any files. Used for testing and operator preview.

**Actions after prompts:**

1. Write `stack/operator/config.yaml` via string template (no pyyaml dependency)
2. `mkdir vault_path` — no-op if exists, warn if non-empty (don't wipe)
3. Print start instructions:
   ```
   Setup complete.
   To start your instance:
     cd ~/lmf/stack
     python -m lmf.orchestrator
   Then open: http://localhost:8002
   ```
4. `"Start now? [y/N]"` — if yes, spawn orchestrator subprocess

**`config.yaml` template written by wizard:**

```yaml
vault_path: {vault_path}
ai_name: {ai_name}
instance_name: {instance_slug}
port: 8002
model: {model}
num_ctx: 8192
timeout_s: 300

backends:
  - name: ollama
    type: ollama
    base_url: http://localhost:11434
    model: {model}
    num_ctx: 8192
    priority: 0
```

### README update

One-liner block at the top of README.md, above the architecture section:

```powershell
# Windows (PowerShell) — paste into terminal
iwr https://github.com/JaredMAllison/lmf/releases/download/v0.1.0/setup.ps1 | iex
```

```bash
# Linux / Mac — paste into terminal
curl -fsSL https://github.com/JaredMAllison/lmf/releases/download/v0.1.0/setup.sh | bash
```

One-liners pin to a **release tag**, never `main` — protects against supply chain risk if `main` is compromised.

---

## Error Handling

| Condition | Response |
|---|---|
| Python missing | Print install URL, exit 1 — do not continue |
| git missing | Print install URL, exit 1 — do not continue |
| Ollama not responding (`ollama list` fails) | "Make sure Ollama is running, then re-run setup." Exit 1 |
| `config.yaml` already exists | "Config found. Overwrite? [y/N]" — N keeps existing, Y proceeds |
| Vault path non-empty | Warn: "Directory exists and is not empty — continuing anyway." Do not delete. |
| Model not in `ollama list` | Never reached — wizard only presents what's available |

---

## File Map

| Action | File |
|---|---|
| Create | `scripts/setup.ps1` |
| Create | `scripts/setup.sh` |
| Create | `scripts/lmf-setup.py` |
| Modify | `README.md` — add one-liner block, update stale repo structure section |

`stack/operator/config.yaml` is written at runtime by the wizard, not committed (already gitignored).

---

## Fritz Bypass

Fritz-tier operators who want full control:

```bash
git clone https://github.com/JaredMAllison/lmf.git ~/lmf
cd ~/lmf
pip install requests pyyaml
python scripts/lmf-setup.py        # run wizard, OR:
cp stack/operator/config.yaml.example stack/operator/config.yaml
# edit config.yaml manually
cd stack && python -m lmf.orchestrator
```

The wizard is always skippable. Manual config is always valid.

---

## Security Notes

- Bootstrap scripts (`setup.ps1`, `setup.sh`) are included in GitHub releases as release artifacts, not served from `main` branch directly
- One-liners in README pin to a specific release tag (`v0.1.0`), updated with each release
- `setup.py` naming avoided — renamed `lmf-setup.py` to prevent accidental execution by pip/build tooling
- No secrets in any committed file — `config.yaml` is gitignored, API keys are env vars

---

## Testing

- `lmf-setup.py --dry-run` — prints what would be written without creating files. Enables unit testing of the config template rendering.
- Wizard prompts are extracted into pure functions (`build_config(vault_path, ai_name, model) -> str`) so they can be tested without interactive input.
- Bootstrap scripts are integration-tested manually against a clean VM or container snapshot.
- Existing `pytest` suite (`python -m pytest features/feature_manager/tests/ -v`) must pass after any changes to the repo structure these scripts create.
