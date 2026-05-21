import json
import sys
from pathlib import Path
from features.feature_manager.init_wizard import (
    detect_os,
    detect_wsl,
    suggest_vault_root,
)


def test_detect_os_returns_string():
    plat = detect_os()
    assert plat in ("linux", "windows", "macos")


def test_detect_wsl_returns_bool():
    is_wsl = detect_wsl()
    assert isinstance(is_wsl, bool)


def test_suggest_vault_root_returns_string():
    path = suggest_vault_root()
    assert isinstance(path, str)
    assert len(path) > 5


def test_suggest_vault_root_is_absolute():
    path = suggest_vault_root()
    # Should look like an absolute path
    assert "/" in path or "\\" in path


def test_setup_lock_symlink_creates_vault_lock(tmp_path):
    from features.feature_manager.init_wizard import setup_lock_symlink

    vault = tmp_path / "myvault"
    vault.mkdir()
    lmf_home = tmp_path / "dot-lmf"

    setup_lock_symlink(vault, lmf_home=lmf_home)

    lock = vault / "installed-lock.json"
    assert lock.exists()
    data = json.loads(lock.read_text())
    assert data == {"version": 1, "entries": []}


def test_setup_lock_symlink_creates_symlink(tmp_path):
    from features.feature_manager.init_wizard import setup_lock_symlink

    vault = tmp_path / "myvault"
    vault.mkdir()
    lmf_home = tmp_path / "dot-lmf"

    setup_lock_symlink(vault, lmf_home=lmf_home)

    symlink = lmf_home / "installed-lock.json"
    assert symlink.is_symlink()
    assert symlink.resolve() == (vault / "installed-lock.json").resolve()


def test_setup_lock_symlink_does_not_overwrite_existing_lock(tmp_path):
    from features.feature_manager.init_wizard import setup_lock_symlink

    vault = tmp_path / "myvault"
    vault.mkdir()
    existing = vault / "installed-lock.json"
    existing.write_text(json.dumps({"version": 1, "entries": [{"name": "panel.x"}]}))
    lmf_home = tmp_path / "dot-lmf"

    setup_lock_symlink(vault, lmf_home=lmf_home)

    data = json.loads(existing.read_text())
    assert data["entries"][0]["name"] == "panel.x"


def test_setup_lock_symlink_replaces_stale_symlink(tmp_path):
    from features.feature_manager.init_wizard import setup_lock_symlink

    vault = tmp_path / "myvault"
    vault.mkdir()
    lmf_home = tmp_path / "dot-lmf"
    lmf_home.mkdir()

    stale = lmf_home / "installed-lock.json"
    stale.symlink_to("/nonexistent/path/lock.json")

    setup_lock_symlink(vault, lmf_home=lmf_home)

    assert stale.is_symlink()
    assert stale.resolve() == (vault / "installed-lock.json").resolve()
