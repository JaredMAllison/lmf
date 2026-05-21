# LMF Setup — Manual

This is the manual setup path. An automated one-liner is coming. Use this for now.

**Time:** ~10 minutes  
**Prerequisites:** Ollama installed and running, Python 3.x, git

---

## 1. Clone the repo

```bash
git clone https://github.com/JaredMAllison/lmf.git ~/lmf
cd ~/lmf
```

**Windows:**
```powershell
git clone https://github.com/JaredMAllison/lmf.git $HOME\lmf
cd $HOME\lmf
```

---

## 2. Install dependencies

```bash
pip install requests pyyaml
```

---

## 3. Check what Ollama models you have

```bash
ollama list
```

If the list is empty, pull a model first:

```bash
ollama pull qwen2.5:7b
```

---

## 4. Create your operator config

```bash
cp stack/operator/config.yaml.example stack/operator/config.yaml
```

Open `stack/operator/config.yaml` and set three fields:

```yaml
vault_path: /home/yourname/lmf-vault   # where your vault will live
ai_name: YourAssistant                  # what you'll call your assistant
model: qwen2.5:7b                       # match what's in `ollama list`
```

Leave everything else at defaults for now.

**Windows paths** use backslashes or forward slashes — both work in this config:
```yaml
vault_path: C:\Users\yourname\lmf-vault
```

---

## 5. Create your vault directory

```bash
mkdir ~/lmf-vault
```

**Windows:**
```powershell
mkdir $HOME\lmf-vault
```

The vault starts empty. No `VAULT.md` means the orchestrator starts in init mode — your assistant will introduce itself and walk you through setup.

---

## 6. Start the orchestrator

```bash
cd stack
python -m lmf.orchestrator
```

Then open: **http://localhost:8002**

Your assistant is running. Talk to it. It will handle the rest.

---

## 7. (Optional) Explore the codebase with Claude Code

Open a second terminal, go back to the repo root, and start a Claude Code session:

```bash
cd ~/lmf
claude
```

Claude Code reads `CLAUDE.md` (architect context) and `opencode.md` (engineer context). You're in Big Pickle mode — engineer role, implementation focus. The Covenant and codebase map are already loaded.

Good starting questions:
- "Walk me through the orchestrator's request lifecycle"
- "What does the Feature Manager install flow look like end to end?"
- "Where would I add a new backend type?"

---

## Troubleshooting

**Orchestrator won't start:** Make sure you're running from the `stack/` directory, not the repo root. The import path requires it: `cd stack && python -m lmf.orchestrator`

**Ollama connection refused:** Ollama needs to be running. On Windows, check the system tray. On Linux: `ollama serve`

**Model not found:** Run `ollama list` to confirm the model name exactly matches what's in `config.yaml`
