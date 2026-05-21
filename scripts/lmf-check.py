#!/usr/bin/env python3
"""
lmf-check.py — Check LMF setup status.

Reports what's done, what's missing, and the exact command to fix each gap.
Re-run after fixing anything until all checks pass.

Usage:
    python scripts/lmf-check.py
"""

import subprocess
import sys
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "stack" / "operator" / "config.yaml"

PASS = "  ✓"
FAIL = "  ✗"


def run(cmd, timeout=5):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0, r.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, ""


def check(label, ok, fix=None):
    print(f"{PASS if ok else FAIL}  {label}")
    if not ok and fix:
        print(f"       → {fix}")
    return ok


def main():
    issues = 0

    print(f"\nLMF Setup Check\n{'─' * 44}")
    print(f"Repo: {REPO_ROOT}\n")

    # Python
    py_ok = sys.version_info >= (3, 10)
    if not check(f"Python 3.10+  (have {sys.version.split()[0]})", py_ok,
                 "Install from https://python.org/downloads"):
        issues += 1

    # git
    git_ok, _ = run(["git", "--version"])
    if not check("git installed", git_ok, "Install from https://git-scm.com"):
        issues += 1

    # requests
    try:
        import requests
        req_ok = True
    except ImportError:
        req_ok = False
    if not check("requests installed", req_ok, "pip install requests"):
        issues += 1

    # pyyaml
    try:
        import yaml
        yaml_ok = True
    except ImportError:
        yaml_ok = False
    if not check("pyyaml installed", yaml_ok, "pip install pyyaml"):
        issues += 1

    # config.yaml exists
    config_exists = CONFIG_PATH.exists()
    if not check("config.yaml exists", config_exists,
                 "cp stack/operator/config.yaml.example stack/operator/config.yaml"):
        issues += 1

    # config.yaml is filled in (not still showing placeholder values)
    if config_exists:
        content = CONFIG_PATH.read_text()
        configured = "/path/to/your/vault" not in content and "YourAssistant" not in content
        if not check("config.yaml filled in (vault_path + ai_name set)", configured,
                     "Edit stack/operator/config.yaml — set vault_path and ai_name"):
            issues += 1
        else:
            configured = True

        # vault directory exists
        if yaml_ok and configured:
            try:
                cfg = yaml.safe_load(content)
                vault_path = Path(os.path.expandvars(cfg.get("vault_path", ""))).expanduser()
                vault_exists = vault_path.exists()
                if not check(f"vault directory exists  ({vault_path})", vault_exists,
                             f"mkdir \"{vault_path}\""):
                    issues += 1
            except Exception as e:
                print(f"{FAIL}  vault_path readable  ({e})")
                issues += 1
    else:
        configured = False

    # Ollama running
    ollama_ok, ollama_out = run(["ollama", "list"])
    if not check("Ollama running", ollama_ok,
                 "Start Ollama — system tray on Windows, or 'ollama serve' on Linux"):
        issues += 1

    # Model pulled
    if ollama_ok and config_exists and yaml_ok:
        try:
            cfg = yaml.safe_load(CONFIG_PATH.read_text())
            model = cfg.get("model", "").strip()
            if model:
                model_name = model.split(":")[0]
                model_ok = model_name in ollama_out
                if not check(f"model available  ({model})", model_ok,
                             f"ollama pull {model}"):
                    issues += 1
        except Exception:
            pass

    print(f"\n{'─' * 44}")
    if issues == 0:
        print("All checks passed.\n")
        print("Start your instance:")
        print("  cd stack")
        print("  python -m lmf.orchestrator")
        print("  → http://localhost:8002\n")
        print("Claude Code session (second terminal):")
        print(f"  cd {REPO_ROOT}")
        print("  claude\n")
    else:
        print(f"{issues} issue(s) to fix. Run the → commands above, then re-run:\n")
        print("  python scripts/lmf-check.py\n")


if __name__ == "__main__":
    main()
