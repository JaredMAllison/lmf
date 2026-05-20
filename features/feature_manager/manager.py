import json
import sys
import os
import subprocess
import tempfile
import shutil
import urllib.request
import urllib.error
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent.parent / "schema" / "package-manifest.schema.json"
PANELS_REGISTRY = Path(__file__).parent.parent / "panels" / "catalog.json"
SKILLS_REGISTRY = Path(__file__).parent.parent / "skills" / "catalog.json"

WORKSPACE_DIR = Path(os.getenv("LMF_WORKSPACE", "/tmp/lmf-install"))
INSTALLED_MANIFEST = WORKSPACE_DIR / "installed.json"
LOCK_FILE = Path(os.getenv("LMF_LOCK_FILE", str(Path.home() / ".lmf" / "installed-lock.json")))


def load_schema(path=None):
    path = path or SCHEMA_PATH
    with open(path) as f:
        return json.load(f)


def load_registry(path):
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, list):
        return data  # flat array format (legacy)
    if isinstance(data, dict):
        # Nested format — extract the array by known key
        for key in ("panels", "skills"):
            if key in data:
                return data[key]
    return data


def validate_manifest(manifest, schema=None):
    try:
        import jsonschema
    except ImportError:
        print("jsonschema is required. Run: pip install jsonschema")
        sys.exit(1)

    schema = schema or load_schema()
    try:
        jsonschema.validate(manifest, schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"Validation error: {e.message}")
        print(f"Path: {' → '.join(str(p) for p in e.absolute_path)}")
        return False


def validate_registry(path, schema=None):
    schema = schema or load_schema()
    registry = load_registry(path)
    errors = []
    for i, entry in enumerate(registry):
        if not validate_manifest(entry, schema):
            errors.append((i, entry.get("name", f"entry-{i}")))
    return errors


def cmd_validate(args):
    schema = load_schema()
    panels_errs = validate_registry(PANELS_REGISTRY, schema)
    skills_errs = validate_registry(SKILLS_REGISTRY, schema)
    all_ok = True

    for path, errs, label in [
        (PANELS_REGISTRY, panels_errs, "panels"),
        (SKILLS_REGISTRY, skills_errs, "skills"),
    ]:
        if errs:
            print(f"{label} registry ({path}): {len(errs)} invalid entries")
            for idx, name in errs:
                print(f"  [{idx}] {name}")
            all_ok = False
        else:
            print(f"{label} registry ({path}): all valid")

    if all_ok:
        print("\nAll manifests valid.")
    else:
        sys.exit(1)


def cmd_list(args):
    """List catalog entries with optional --type and --status filters."""
    type_filter = args.get("type")
    status_filter = args.get("status")

    try:
        entries = load_registry(PANELS_REGISTRY)
    except FileNotFoundError:
        print(f"Catalog not found: {PANELS_REGISTRY}")
        sys.exit(1)

    if type_filter:
        entries = [e for e in entries if e.get("type") == type_filter]
    if status_filter:
        entries = [e for e in entries if e.get("status") == status_filter]

    if not entries:
        print("No packages match.")
        return

    col_w = {"name": 30, "type": 8, "trust": 10, "status": 12}
    header = f"{'Name':<{col_w['name']}} {'Type':<{col_w['type']}} {'Trust':<{col_w['trust']}} {'Status':<{col_w['status']}} Description"
    print(header)
    print("-" * (len(header) + 20))
    for e in entries:
        print(
            f"{e.get('name',''):<{col_w['name']}} "
            f"{e.get('type',''):<{col_w['type']}} "
            f"{e.get('trust_level',''):<{col_w['trust']}} "
            f"{e.get('status',''):<{col_w['status']}} "
            f"{e.get('description','')[:60]}"
        )


def resolve_placeholders(text):
    """Replace {{NAME}} placeholders with environment variable values."""
    import re
    def replace(m):
        key = m.group(1)
        return os.getenv(key, m.group(0))
    return re.sub(r"\{\{(\w+)\}\}", replace, text)


def clone_source(source, dest):
    """Clone a git repo or copy a local path into dest."""
    if "git" in source:
        url = resolve_placeholders(source["git"])
        print(f"  Cloning {url}...")
        result = subprocess.run(
            ["git", "clone", "--depth=1", url, str(dest)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  Clone failed: {result.stderr.strip()}")
            return False
        print(f"  Cloned to {dest}")
        return True

    elif "path" in source:
        src_path = Path(resolve_placeholders(source["path"]))
        if not src_path.exists():
            print(f"  Source path not found: {src_path}")
            return False
        dest.mkdir(parents=True, exist_ok=True)
        if src_path.is_file():
            shutil.copy2(src_path, dest / src_path.name)
            print(f"  Copied {src_path} to {dest}")
        elif src_path.is_dir():
            shutil.copytree(src_path, dest, dirs_exist_ok=True)
            print(f"  Copied directory {src_path} to {dest}")
        return True
    return True


def record_installed(manifest):
    """Record an installed package in the installed manifest."""
    name = manifest.get("name", "unknown")
    existing = {}
    if INSTALLED_MANIFEST.exists():
        existing = json.loads(INSTALLED_MANIFEST.read_text())
    existing[name] = {
        "name": name,
        "source": manifest.get("source", {}),
        "install": manifest.get("install", []),
        "health_endpoint": manifest.get("health_endpoint", ""),
        "updated": None,
    }
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    INSTALLED_MANIFEST.write_text(json.dumps(existing, indent=2))
    print(f"  Recorded {name} in installed manifest.")


def write_lock_file(manifest, lock_path=None):
    """Write an installed package entry to the persistent lock file (upsert by name)."""
    from datetime import datetime, timezone
    if lock_path:
        path = Path(lock_path)
    else:
        env_lock = os.getenv("LMF_LOCK_FILE")
        path = Path(env_lock) if env_lock else LOCK_FILE
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {"version": 1, "entries": []}
    if path.exists():
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            data = {"version": 1, "entries": []}

    entries = [e for e in data.get("entries", []) if e.get("name") != manifest.get("name")]

    entry = {
        "name": manifest.get("name", "unknown"),
        "version": manifest.get("version", "0.0.0"),
        "source": manifest.get("source", {}),
        "installed_at": datetime.now(timezone.utc).isoformat(),
    }
    if manifest.get("panel_entry") is not None:
        entry["panel_entry"] = manifest["panel_entry"]
    if manifest.get("health_endpoint") is not None:
        entry["health_endpoint"] = manifest["health_endpoint"]

    entries.append(entry)
    data["entries"] = entries
    path.write_text(json.dumps(data, indent=2))


LMF_MANIFEST_SCHEMA_PATH = Path(__file__).parent.parent / "schema" / "lmf-manifest.schema.json"


def install_from_catalog(name, catalog=None):
    """Look up a package in the catalog, fetch its lmf-manifest.json, install it."""
    if catalog is None:
        catalog = load_registry(PANELS_REGISTRY)

    entry = next((e for e in catalog if e.get("name") == name), None)
    if not entry:
        print(f"Package '{name}' not found in catalog.")
        return False

    if entry.get("status") == "Planned":
        print(f"Package '{name}' is Planned (not yet installable).")
        return False

    source = entry.get("source", {})
    with tempfile.TemporaryDirectory() as tmp:
        pkg_dir = Path(tmp) / name.replace(".", "-")
        if not clone_source(source, pkg_dir):
            return False

        manifest_path = pkg_dir / "lmf-manifest.json"
        if not manifest_path.exists():
            print(f"No lmf-manifest.json found in '{name}' repo. The package must ship one.")
            return False

        manifest = json.loads(manifest_path.read_text())
        lmf_schema = json.loads(LMF_MANIFEST_SCHEMA_PATH.read_text())
        if not validate_manifest(manifest, lmf_schema):
            print(f"lmf-manifest.json in '{name}' is invalid.")
            return False

        return install_single(manifest)


def install_single(manifest):
    """Install a single validated manifest entry."""
    name = manifest.get("name", "unknown")
    print(f"Installing {name}...")

    source = manifest.get("source", {})
    install_steps = manifest.get("install", [])

    # Clone or copy source
    if source:
        WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
        pkg_dir = WORKSPACE_DIR / name.replace(".", "-")
        if pkg_dir.exists():
            shutil.rmtree(pkg_dir)
        if not clone_source(source, pkg_dir):
            return False
    else:
        pkg_dir = None

    # Run install steps from the package directory
    cwd = str(pkg_dir) if pkg_dir else None
    for step in install_steps:
        resolved = resolve_placeholders(step)
        print(f"  Running: {resolved}")
        result = subprocess.run(
            resolved, shell=True, capture_output=True, text=True,
            cwd=cwd
        )
        if result.returncode != 0:
            print(f"  Step failed (exit {result.returncode})")
            if result.stderr:
                print(f"  stderr: {result.stderr.strip()}")
            return False
        if result.stdout:
            for line in result.stdout.strip().splitlines():
                print(f"    {line}")

    print(f"  {name} installed successfully.")
    write_lock_file(manifest)
    return True


def cmd_install(args):
    name = args.get("name")
    manifest_file = args.get("manifest") or args.get("profile")

    if name:
        catalog = load_registry(PANELS_REGISTRY)
        if not install_from_catalog(name, catalog=catalog):
            sys.exit(1)
        return

    if not manifest_file:
        print("Usage: manager.py install --name <package> | --manifest <file> | --profile <file>")
        sys.exit(1)

    with open(manifest_file) as f:
        raw = f.read()
    raw = resolve_placeholders(raw)

    data = json.loads(raw)
    schema = load_schema()

    # Seed profile with multiple manifests, or a single manifest
    if isinstance(data, list):
        manifests = data
    elif "panels" in data or "skills" in data:
        # Seed profile referencing registry entries by name
        manifests = resolve_seed_profile(data, schema)
    else:
        manifests = [data]

    successes = 0
    failures = []
    for manifest in manifests:
        if validate_manifest(manifest, schema):
            if install_single(manifest):
                successes += 1
            else:
                failures.append(manifest.get("name", "unknown"))
        else:
            failures.append(manifest.get("name", "unknown"))

    print(f"\nInstall complete: {successes} installed, {len(failures)} failed")
    if failures:
        print(f"Failed: {', '.join(failures)}")
        sys.exit(1)


def resolve_seed_profile(profile, schema):
    """Resolve registry name references in a seed profile to full manifests."""
    panel_registry = load_registry(PANELS_REGISTRY)
    skill_registry = load_registry(SKILLS_REGISTRY)

    registry_by_name = {}
    for entry in panel_registry + skill_registry:
        registry_by_name[entry["name"]] = entry

    manifests = []
    for ref in profile.get("panels", []):
        if ref in registry_by_name:
            manifests.append(registry_by_name[ref])
        else:
            print(f"  Warning: panel '{ref}' not found in registry")

    for ref in profile.get("skills", []):
        if ref in registry_by_name:
            manifests.append(registry_by_name[ref])
        else:
            print(f"  Warning: skill '{ref}' not found in registry")

    return manifests


def update_single(entry):
    """Update a single installed package: pull source, re-run install, verify health."""
    name = entry.get("name", "unknown")
    print(f"Updating {name}...")

    source = entry.get("source", {})
    pkg_dir = WORKSPACE_DIR / name.replace(".", "-")

    if "git" in source:
        if pkg_dir.exists():
            # Pull latest
            print(f"  Pulling latest in {pkg_dir}...")
            result = subprocess.run(
                ["git", "pull"], capture_output=True, text=True,
                cwd=str(pkg_dir)
            )
            if result.returncode != 0:
                print(f"  Git pull failed: {result.stderr.strip()}")
                return False
            for line in result.stdout.strip().splitlines():
                print(f"    {line}")
        else:
            # Repo was deleted; re-clone
            print(f"  Directory missing, re-cloning...")
            if not clone_source(source, pkg_dir):
                return False
    elif "path" in source:
        # Re-copy from source path
        print(f"  Re-copying from {source.get('path')}...")
        if pkg_dir.exists():
            shutil.rmtree(pkg_dir)
        if not clone_source(source, pkg_dir):
            return False

    # Re-run install steps
    install_steps = entry.get("install", [])
    if install_steps:
        cwd = str(pkg_dir) if pkg_dir.exists() else None
        for step in install_steps:
            resolved = resolve_placeholders(step)
            print(f"  Running: {resolved}")
            result = subprocess.run(
                resolved, shell=True, capture_output=True, text=True,
                cwd=cwd
            )
            if result.returncode != 0:
                print(f"  Step failed (exit {result.returncode})")
                if result.stderr:
                    print(f"  stderr: {result.stderr.strip()}")
                return False
    else:
        print(f"  No install steps defined, source updated.")

    # Health check
    health_url = entry.get("health_endpoint", "")
    if health_url:
        print(f"  Verifying health at {health_url}...")
        health_url = resolve_placeholders(health_url)
        cmd_health_check({"name": name, "url": health_url})

    print(f"  {name} updated successfully.")
    return True


def cmd_update(args):
    """Update all or specified installed packages."""
    if not INSTALLED_MANIFEST.exists():
        print("No installed packages found. Nothing to update.")
        return

    installed = json.loads(INSTALLED_MANIFEST.read_text())

    # Filter to specific packages if --name was given
    filter_name = args.get("name")
    if filter_name:
        if filter_name in installed:
            entries = {filter_name: installed[filter_name]}
        else:
            print(f"Package '{filter_name}' not found in installed manifest.")
            sys.exit(1)
    else:
        entries = installed

    if not entries:
        print("No packages to update.")
        return

    successes = 0
    failures = []
    for name, entry in entries.items():
        if update_single(entry):
            successes += 1
            # Update the timestamp
            installed[name]["updated"] = subprocess.run(
                ["date", "-Iseconds"], capture_output=True, text=True
            ).stdout.strip()
        else:
            failures.append(name)

    INSTALLED_MANIFEST.write_text(json.dumps(installed, indent=2))

    print(f"\nUpdate complete: {successes} updated, {len(failures)} failed")
    if failures:
        print(f"Failed: {', '.join(failures)}")
        sys.exit(1)


def cmd_populate_panels(args):
    cfg_path = args.get("config") or "public/panels_config.json"
    try:
        with open(cfg_path) as f:
            cfg = json.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {cfg_path}")
        sys.exit(1)

    for panel in cfg.get("panels", []):
        for key, val in list(panel.items()):
            if isinstance(val, str) and "{{" in val:
                env_name = val.strip("{}")
                panel[key] = os.getenv(env_name, "")
                if not panel[key]:
                    print(f"  Warning: no env var set for {env_name}")

    with open(cfg_path, "w") as f:
        json.dump(cfg, f, indent=2)

    unresolved = [
        p["id"] for p in cfg.get("panels", [])
        if any(v == "" for v in p.values() if isinstance(v, str))
    ]
    if unresolved:
        print(f"Panels with unresolved fields: {unresolved}")
    else:
        print("All panel config populated.")


def cmd_health_check(args):
    name = args.get("name", "unknown")
    url = args.get("url")
    if not url:
        print("Usage: manager.py health-check --name <package> --url <health_endpoint>")
        sys.exit(1)

    url = resolve_placeholders(url)
    print(f"Checking {name} at {url}...")
    try:
        resp = urllib.request.urlopen(url, timeout=10)
        body = resp.read().decode()
        print(f"  HTTP {resp.status} — {body[:200]}")
        return True
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} — {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"  Connection failed: {e.reason}")
        return False


def cmd_health_check_wrapper(args):
    if cmd_health_check(args):
        print("Health check passed.")
    else:
        print("Health check failed.")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: manager.py <command> [args...]")
        print("Commands:")
        print("  validate              Validate all registry files against the schema")
        print("  list [--type <type>] [--status <status>]")
        print("                        List catalog entries")
        print("  install --name <package>  Install a package from the catalog by name")
        print("          --manifest <file> Install from a local manifest file")
        print("          --profile <file>  Install all packages in a seed profile")
        print("  populate-panels       Resolve {{ENV_VAR}} placeholders in panels_config.json")
        print("  health-check --name <package> --url <health_endpoint>")
        print("                        Verify a service health endpoint is responding")
        print("  init                  Run the interactive init wizard to create a seed profile")
        print("  update [--name <package>]")
        print("                        Update all installed packages (or a specific one)")
        sys.exit(1)

    cmd = sys.argv[1]
    args = {}
    for i in range(2, len(sys.argv), 2):
        if i + 1 < len(sys.argv):
            key = sys.argv[i].lstrip("-")
            args[key] = sys.argv[i + 1]

    if cmd == "validate":
        cmd_validate(args)
    elif cmd == "list":
        cmd_list(args)
    elif cmd == "install":
        cmd_install(args)
    elif cmd == "populate-panels":
        cmd_populate_panels(args)
    elif cmd == "health-check":
        cmd_health_check_wrapper(args)
    elif cmd == "init":
        from .init_wizard import run_wizard
        run_wizard(args.get("output"))
    elif cmd == "update":
        cmd_update(args)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
