import json
import pytest
from pathlib import Path
from features.feature_manager.manager import (
    load_schema,
    load_registry,
    validate_manifest,
    validate_registry,
    resolve_seed_profile,
    resolve_placeholders,
    PANELS_REGISTRY,
    SKILLS_REGISTRY,
)

SCHEMA_PATH = Path(__file__).parent.parent.parent / "schema" / "package-manifest.schema.json"


def test_schema_loads():
    schema = load_schema(SCHEMA_PATH)
    assert schema["title"] == "LMF Package Manifest"
    assert "properties" in schema


def test_panel_manifest_passes():
    schema = load_schema(SCHEMA_PATH)
    manifest = {
        "name": "panel.test",
        "version": "1.0.0",
        "type": "panel",
        "description": "Test panel",
        "source": {"git": "{{GIT_ORG}}/test.git"},
        "install": ["echo ok"],
        "dependencies": [],
        "panel_entry": {"host": "localhost", "port": 9999, "route": "/test"},
        "health_endpoint": "/health",
        "trust_level": "Solo",
        "status": "Experimental",
        "tags": ["test"],
    }
    assert validate_manifest(manifest, schema) is True


def test_manifest_missing_type_fails():
    schema = load_schema(SCHEMA_PATH)
    manifest = {"name": "bad", "version": "1.0.0"}
    assert validate_manifest(manifest, schema) is False


def test_manifest_bad_version_fails():
    schema = load_schema(SCHEMA_PATH)
    manifest = {
        "name": "bad",
        "version": "not-semver",
        "type": "panel",
    }
    assert validate_manifest(manifest, schema) is False


def test_manifest_bad_type_fails():
    schema = load_schema(SCHEMA_PATH)
    manifest = {
        "name": "bad",
        "version": "1.0.0",
        "type": "not-a-valid-type",
    }
    assert validate_manifest(manifest, schema) is False


def test_registry_validation_panels():
    errors = validate_registry(PANELS_REGISTRY)
    assert errors == [], f"Panel registry has {len(errors)} invalid entries: {errors}"


def test_registry_validation_skills():
    errors = validate_registry(SKILLS_REGISTRY)
    assert errors == [], f"Skill registry has {len(errors)} invalid entries: {errors}"


def test_resolve_placeholders_env_set(monkeypatch):
    monkeypatch.setenv("TEST_VAL", "resolved")
    result = resolve_placeholders("{{TEST_VAL}}/path")
    assert result == "resolved/path"


def test_resolve_placeholders_env_missing():
    result = resolve_placeholders("{{MISSING_VAR}}/path")
    assert result == "{{MISSING_VAR}}/path"


def test_resolve_seed_profile():
    schema = load_schema(SCHEMA_PATH)
    profile = {
        "panels": ["panel.marlin"],
        "skills": ["skill.marlin-capture"],
    }
    manifests = resolve_seed_profile(profile, schema)
    names = [m["name"] for m in manifests]
    assert "panel.marlin" in names
    assert "skill.marlin-capture" in names
    assert len(manifests) == 2


def test_resolve_seed_profile_unknown_skill():
    schema = load_schema(SCHEMA_PATH)
    profile = {
        "panels": [],
        "skills": ["skill.nonexistent"],
    }
    manifests = resolve_seed_profile(profile, schema)
    assert manifests == []


import tempfile, os


def test_write_lock_file_creates_entry():
    from features.feature_manager.manager import write_lock_file
    manifest = {
        "name": "panel.test",
        "version": "1.0.0",
        "source": {"git": "https://github.com/example/test.git"},
        "panel_entry": {"host": "localhost", "port": 9999, "route": "/test"},
        "health_endpoint": "/health"
    }
    with tempfile.TemporaryDirectory() as tmp:
        lock_path = os.path.join(tmp, "lmf-lock.json")
        write_lock_file(manifest, lock_path=lock_path)
        import json
        data = json.load(open(lock_path))
        assert data["version"] == 1
        assert len(data["entries"]) == 1
        assert data["entries"][0]["name"] == "panel.test"
        assert data["entries"][0]["version"] == "1.0.0"
        assert "T" in data["entries"][0]["installed_at"]  # UTC datetime, not date-only


def test_write_lock_file_appends():
    from features.feature_manager.manager import write_lock_file
    import json
    with tempfile.TemporaryDirectory() as tmp:
        lock_path = os.path.join(tmp, "lmf-lock.json")
        for name in ["panel.one", "panel.two"]:
            write_lock_file({"name": name, "version": "1.0.0", "source": {}}, lock_path=lock_path)
        data = json.load(open(lock_path))
        assert len(data["entries"]) == 2
        assert {e["name"] for e in data["entries"]} == {"panel.one", "panel.two"}


def test_write_lock_file_upserts():
    from features.feature_manager.manager import write_lock_file
    import json
    with tempfile.TemporaryDirectory() as tmp:
        lock_path = os.path.join(tmp, "lmf-lock.json")
        write_lock_file({"name": "panel.test", "version": "1.0.0", "source": {}}, lock_path=lock_path)
        write_lock_file({"name": "panel.test", "version": "1.1.0", "source": {}}, lock_path=lock_path)
        data = json.load(open(lock_path))
        assert len(data["entries"]) == 1
        assert data["entries"][0]["version"] == "1.1.0"


def test_write_lock_file_omits_null_fields():
    from features.feature_manager.manager import write_lock_file
    import json
    with tempfile.TemporaryDirectory() as tmp:
        lock_path = os.path.join(tmp, "lmf-lock.json")
        write_lock_file({"name": "skill.test", "version": "1.0.0", "source": {}}, lock_path=lock_path)
        data = json.load(open(lock_path))
        entry = data["entries"][0]
        assert "panel_entry" not in entry
        assert "health_endpoint" not in entry
