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


def test_cmd_list_returns_all(capsys):
    from features.feature_manager.manager import cmd_list
    cmd_list({})
    captured = capsys.readouterr()
    assert "panel.marlin" in captured.out


def test_cmd_list_filters_by_type(capsys):
    from features.feature_manager.manager import cmd_list
    cmd_list({"type": "panel"})
    captured = capsys.readouterr()
    assert "panel" in captured.out


def test_cmd_list_filters_by_status(capsys):
    from features.feature_manager.manager import cmd_list
    cmd_list({"status": "Experimental"})
    captured = capsys.readouterr()
    assert "Experimental" in captured.out


def test_cmd_list_planned_visible(capsys):
    from features.feature_manager.manager import cmd_list
    cmd_list({"status": "Planned"})
    captured = capsys.readouterr()
    assert "panel.rpg" in captured.out


import json as _json


def test_install_name_requires_name_or_manifest():
    from features.feature_manager.manager import cmd_install
    import pytest
    with pytest.raises(SystemExit):
        cmd_install({})


def test_install_name_catalog_lookup_missing(capsys):
    from features.feature_manager.manager import install_from_catalog
    result = install_from_catalog("panel.doesnotexist", catalog=[])
    assert result is False
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_install_name_blocks_planned(capsys):
    from features.feature_manager.manager import install_from_catalog
    catalog = [{"name": "panel.rpg", "version": "0.1.0", "type": "panel",
                "source": {"git": "https://example.com/rpg.git"}, "status": "Planned"}]
    result = install_from_catalog("panel.rpg", catalog=catalog)
    assert result is False
    captured = capsys.readouterr()
    assert "Planned" in captured.out


def test_install_name_reads_lmf_manifest(tmp_path, monkeypatch):
    from features.feature_manager.manager import install_from_catalog
    manifest_content = {
        "name": "panel.test",
        "version": "1.0.0",
        "type": "panel",
        "install": [],
        "health_endpoint": "/health"
    }
    (tmp_path / "lmf-manifest.json").write_text(_json.dumps(manifest_content))

    catalog = [{
        "name": "panel.test",
        "version": "1.0.0",
        "type": "panel",
        "source": {"path": str(tmp_path)},
        "trust_level": "Solo",
        "status": "Experimental"
    }]

    lock_path = tmp_path / "lock.json"
    monkeypatch.setenv("LMF_LOCK_FILE", str(lock_path))
    result = install_from_catalog("panel.test", catalog=catalog)
    assert result is True
    data = _json.loads(lock_path.read_text())
    assert data["version"] == 1
    assert data["entries"][0]["name"] == "panel.test"


def test_install_name_missing_manifest_errors(tmp_path, capsys):
    from features.feature_manager.manager import install_from_catalog
    catalog = [{
        "name": "panel.test",
        "version": "1.0.0",
        "type": "panel",
        "source": {"path": str(tmp_path)},
        "status": "Experimental"
    }]
    result = install_from_catalog("panel.test", catalog=catalog)
    assert result is False
    captured = capsys.readouterr()
    assert "lmf-manifest.json" in captured.out
