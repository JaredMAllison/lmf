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
