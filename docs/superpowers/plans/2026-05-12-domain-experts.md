# Domain Experts — Feature Manager Extension Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `domain-expert` as a new installable feature type in the LMF Feature Manager — with a classifier, context template, and PROMPT.md convention — without touching the orchestrator wiring.

**Architecture:** The existing Feature Manager handles panels and skills via JSON registries, a JSON Schema validator, a seed profile resolver, and an init wizard. This plan adds `domain-expert` as a third feature type by extending the schema with new conditional fields, creating a parallel registry, and wiring the resolver and wizard to handle the new type identically to existing types.

**Tech Stack:** Python 3, jsonschema, pytest, PyYAML, JSON Schema draft-07

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `features/schema/package-manifest.schema.json` | Modify | Accept `domain-expert` type with `classifier` + `context_template` |
| `features/domain-experts/registry.json` | Create | Domain expert registry (parallel to skills/panels) |
| `features/domain-experts/scheduler/PROMPT.md` | Create | Example domain expert — proves the pattern |
| `features/feature_manager/manager.py` | Modify | `DOMAIN_EXPERTS_REGISTRY` constant, `resolve_seed_profile`, `cmd_validate` |
| `features/feature_manager/init_wizard.py` | Modify | `SEED_TEMPLATE` + domain experts phase in `run_wizard` |
| `features/feature_manager/tests/test_validation.py` | Modify | Domain expert schema + registry + resolver tests |
| `features/feature_manager/tests/test_init_wizard.py` | Modify | SEED_TEMPLATE domain experts block test |

---

## Task 1: Schema Extension

**Files:**
- Modify: `features/schema/package-manifest.schema.json`
- Modify: `features/feature_manager/tests/test_validation.py`

- [ ] **Step 1: Write failing tests for domain-expert schema**

Append to `features/feature_manager/tests/test_validation.py`:

```python
def test_domain_expert_manifest_passes():
    schema = load_schema(SCHEMA_PATH)
    manifest = {
        "name": "domain.test",
        "version": "1.0.0",
        "type": "domain-expert",
        "description": "Test domain expert",
        "source": {"path": "/tmp/test-expert/"},
        "classifier": {
            "keywords": ["test", "example"],
            "description": "Handles test queries"
        },
        "context_template": {
            "paths": ["Tasks/*.md"],
            "query": "{{operator_message}}"
        },
        "install": [],
        "dependencies": [],
        "trust_level": "Solo",
        "status": "Experimental",
        "tags": ["test"],
    }
    assert validate_manifest(manifest, schema) is True


def test_domain_expert_missing_classifier_fails():
    schema = load_schema(SCHEMA_PATH)
    manifest = {
        "name": "domain.bad",
        "version": "1.0.0",
        "type": "domain-expert",
        "description": "Missing classifier",
        "source": {"path": "/tmp/bad/"},
        "context_template": {"paths": ["Tasks/*.md"]},
        "install": [],
        "dependencies": [],
        "trust_level": "Solo",
        "status": "Experimental",
        "tags": [],
    }
    assert validate_manifest(manifest, schema) is False


def test_domain_expert_empty_context_template_fails():
    schema = load_schema(SCHEMA_PATH)
    manifest = {
        "name": "domain.bad",
        "version": "1.0.0",
        "type": "domain-expert",
        "description": "Empty context template",
        "source": {"path": "/tmp/bad/"},
        "classifier": {"description": "Test"},
        "context_template": {},
        "install": [],
        "dependencies": [],
        "trust_level": "Solo",
        "status": "Experimental",
        "tags": [],
    }
    assert validate_manifest(manifest, schema) is False
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /home/jared/Documents/Obsidian/Marlin
pytest features/feature_manager/tests/test_validation.py::test_domain_expert_manifest_passes features/feature_manager/tests/test_validation.py::test_domain_expert_missing_classifier_fails features/feature_manager/tests/test_validation.py::test_domain_expert_empty_context_template_fails -v
```

Expected: 3 FAILED — `test_domain_expert_manifest_passes` fails because `domain-expert` is not a valid type.

- [ ] **Step 3: Update the schema**

Replace `features/schema/package-manifest.schema.json` with:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "LMF Package Manifest",
  "description": "Schema for LMF panel, skill, plugin, and domain-expert manifests used by the Feature Manager.",
  "type": "object",
  "required": ["name", "version", "type"],
  "properties": {
    "name": {
      "type": "string",
      "description": "Unique identifier for the package (e.g. panel.marlin)"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Semantic version string"
    },
    "type": {
      "type": "string",
      "enum": ["panel", "skill", "plugin", "service", "domain-expert"],
      "description": "Package type"
    },
    "description": {
      "type": "string",
      "description": "Human-readable summary"
    },
    "source": {
      "type": "object",
      "description": "Where to fetch the package source code",
      "properties": {
        "git": { "type": "string", "format": "uri" },
        "path": { "type": "string" },
        "docker": { "type": "string" }
      },
      "oneOf": [
        { "required": ["git"] },
        { "required": ["path"] },
        { "required": ["docker"] }
      ]
    },
    "install": {
      "type": "array",
      "description": "Shell commands to run during installation",
      "items": { "type": "string" }
    },
    "dependencies": {
      "type": "array",
      "description": "Names of other packages required first",
      "items": { "type": "string" }
    },
    "panel_entry": {
      "type": "object",
      "description": "Cockpit panel registration (type=panel only)",
      "properties": {
        "host": { "type": "string" },
        "port": { "type": "integer", "minimum": 1, "maximum": 65535 },
        "route": { "type": "string" }
      }
    },
    "health_endpoint": {
      "type": "string",
      "description": "Relative URL for health checks (e.g. /health)"
    },
    "trust_level": {
      "type": "string",
      "enum": ["Solo", "Vouched", "Validated"],
      "description": "Minimum trust level required"
    },
    "status": {
      "type": "string",
      "enum": ["Experimental", "Stable", "Deprecated"],
      "description": "Feature stability"
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" }
    },
    "classifier": {
      "type": "object",
      "description": "Routing config (type=domain-expert only)",
      "properties": {
        "keywords": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Deterministic fast-path keywords"
        },
        "description": {
          "type": "string",
          "description": "Used by classifier model for ambiguous inputs"
        }
      },
      "required": ["description"],
      "additionalProperties": false
    },
    "context_template": {
      "type": "object",
      "description": "Vault context loading config (type=domain-expert only)",
      "properties": {
        "paths": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Glob patterns for always-loaded structural context"
        },
        "query": {
          "type": "string",
          "description": "Dynamic Loom search query; may include {{operator_message}}"
        }
      },
      "anyOf": [
        { "required": ["paths"] },
        { "required": ["query"] }
      ],
      "additionalProperties": false
    }
  },
  "if": {
    "properties": { "type": { "const": "domain-expert" } },
    "required": ["type"]
  },
  "then": {
    "required": ["classifier", "context_template"]
  },
  "additionalProperties": false
}
```

- [ ] **Step 4: Run all schema tests**

```bash
pytest features/feature_manager/tests/test_validation.py -v
```

Expected: all existing tests PASS, 3 new tests PASS.

- [ ] **Step 5: Commit**

```bash
git add features/schema/package-manifest.schema.json features/feature_manager/tests/test_validation.py
git commit -m "feat: add domain-expert type to manifest schema"
```

---

## Task 2: Domain Experts Directory, Registry, and Example PROMPT.md

**Files:**
- Create: `features/domain-experts/registry.json`
- Create: `features/domain-experts/scheduler/PROMPT.md`
- Modify: `features/feature_manager/tests/test_validation.py`

- [ ] **Step 1: Write failing registry validation test**

Append to `features/feature_manager/tests/test_validation.py`:

```python
def test_registry_validation_domain_experts():
    from features.feature_manager.manager import DOMAIN_EXPERTS_REGISTRY
    errors = validate_registry(DOMAIN_EXPERTS_REGISTRY)
    assert errors == [], f"Domain experts registry has {len(errors)} invalid entries: {errors}"
```

- [ ] **Step 2: Run test to confirm it fails**

```bash
pytest features/feature_manager/tests/test_validation.py::test_registry_validation_domain_experts -v
```

Expected: FAILED — `DOMAIN_EXPERTS_REGISTRY` not defined in manager yet (ImportError or AttributeError).

- [ ] **Step 3: Create the registry file**

Create `features/domain-experts/registry.json`:

```json
[
  {
    "name": "domain.scheduler",
    "version": "1.0.0",
    "type": "domain-expert",
    "description": "Scheduling specialist — tasks, dates, TTF integration",
    "source": { "path": "{{VAULT_ROOT}}/features/domain-experts/scheduler/" },
    "classifier": {
      "keywords": ["schedule", "task", "date", "appointment", "reminder", "when", "goal_date"],
      "description": "Handles time-based questions, task scheduling, and calendar queries"
    },
    "context_template": {
      "paths": ["Tasks/*.md"],
      "query": "{{operator_message}}"
    },
    "install": [],
    "dependencies": [],
    "trust_level": "Solo",
    "status": "Experimental",
    "tags": ["scheduling", "core"]
  }
]
```

- [ ] **Step 4: Create the scheduler PROMPT.md**

Create `features/domain-experts/scheduler/PROMPT.md`:

```markdown
# Scheduler — Domain Expert

You are the Scheduler for this vault. Your job is tasks, dates, and time.

## What you know
- All tasks in the vault with their goal_date, status, start_time, end_time, and context
- TTF integration — tasks with ttf_id are synced to the visual calendar
- Recurrence patterns and available_from fields

## What you do
- Answer questions about what's due, what's scheduled, and when
- Identify tasks that are overdue, unscheduled, or missing TTF sync
- Surface conflicts and gaps in the schedule
- Suggest rescheduling when asked

## What you don't do
- Write to the vault (read-only unless explicitly told otherwise)
- Make decisions about priority — that belongs to the Operator
- Speculate about tasks not in the provided context

## Response style
Precise. Time-anchored. Surface the fact, let the Operator decide what to do with it.
```

- [ ] **Step 5: Add DOMAIN_EXPERTS_REGISTRY constant to manager.py**

In `features/feature_manager/manager.py`, after the `SKILLS_REGISTRY` line (line 13), add:

```python
DOMAIN_EXPERTS_REGISTRY = Path(__file__).parent.parent / "domain-experts" / "registry.json"
```

- [ ] **Step 6: Run the registry test**

```bash
pytest features/feature_manager/tests/test_validation.py::test_registry_validation_domain_experts -v
```

Expected: PASS.

- [ ] **Step 7: Run full test suite to confirm no regressions**

```bash
pytest features/feature_manager/tests/ -v
```

Expected: all tests PASS.

- [ ] **Step 8: Commit**

```bash
git add features/domain-experts/registry.json features/domain-experts/scheduler/PROMPT.md features/feature_manager/manager.py features/feature_manager/tests/test_validation.py
git commit -m "feat: add domain-experts registry and scheduler example"
```

---

## Task 3: manager.py — resolve_seed_profile + cmd_validate

**Files:**
- Modify: `features/feature_manager/manager.py`
- Modify: `features/feature_manager/tests/test_validation.py`

- [ ] **Step 1: Write failing tests for resolve_seed_profile with domain_experts**

Append to `features/feature_manager/tests/test_validation.py`:

```python
def test_resolve_seed_profile_with_domain_experts():
    schema = load_schema(SCHEMA_PATH)
    profile = {
        "panels": [],
        "skills": [],
        "domain_experts": ["domain.scheduler"],
    }
    manifests = resolve_seed_profile(profile, schema)
    names = [m["name"] for m in manifests]
    assert "domain.scheduler" in names
    assert len(manifests) == 1


def test_resolve_seed_profile_unknown_domain_expert():
    schema = load_schema(SCHEMA_PATH)
    profile = {
        "domain_experts": ["domain.nonexistent"],
    }
    manifests = resolve_seed_profile(profile, schema)
    assert manifests == []
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest features/feature_manager/tests/test_validation.py::test_resolve_seed_profile_with_domain_experts features/feature_manager/tests/test_validation.py::test_resolve_seed_profile_unknown_domain_expert -v
```

Expected: both FAILED — `resolve_seed_profile` doesn't load domain experts registry yet.

- [ ] **Step 3: Update resolve_seed_profile in manager.py**

Replace the `resolve_seed_profile` function (currently lines 220-242) with:

```python
def resolve_seed_profile(profile, schema):
    """Resolve registry name references in a seed profile to full manifests."""
    panel_registry = load_registry(PANELS_REGISTRY)
    skill_registry = load_registry(SKILLS_REGISTRY)
    domain_expert_registry = load_registry(DOMAIN_EXPERTS_REGISTRY)

    registry_by_name = {}
    for entry in panel_registry + skill_registry + domain_expert_registry:
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

    for ref in profile.get("domain_experts", []):
        if ref in registry_by_name:
            manifests.append(registry_by_name[ref])
        else:
            print(f"  Warning: domain expert '{ref}' not found in registry")

    return manifests
```

- [ ] **Step 4: Update cmd_validate in manager.py**

Replace the `cmd_validate` function (currently lines 57-78) with:

```python
def cmd_validate(args):
    schema = load_schema()
    panels_errs = validate_registry(PANELS_REGISTRY, schema)
    skills_errs = validate_registry(SKILLS_REGISTRY, schema)
    domain_errs = validate_registry(DOMAIN_EXPERTS_REGISTRY, schema)
    all_ok = True

    for path, errs, label in [
        (PANELS_REGISTRY, panels_errs, "panels"),
        (SKILLS_REGISTRY, skills_errs, "skills"),
        (DOMAIN_EXPERTS_REGISTRY, domain_errs, "domain-experts"),
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
```

- [ ] **Step 5: Run all tests**

```bash
pytest features/feature_manager/tests/ -v
```

Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add features/feature_manager/manager.py features/feature_manager/tests/test_validation.py
git commit -m "feat: extend resolve_seed_profile and cmd_validate for domain experts"
```

---

## Task 4: init_wizard.py — SEED_TEMPLATE + Domain Experts Phase

**Files:**
- Modify: `features/feature_manager/init_wizard.py`
- Modify: `features/feature_manager/tests/test_init_wizard.py`

- [ ] **Step 1: Write failing test for SEED_TEMPLATE**

Append to `features/feature_manager/tests/test_init_wizard.py`:

```python
def test_seed_template_includes_domain_experts():
    from features.feature_manager.init_wizard import SEED_TEMPLATE
    assert "domain_experts:" in SEED_TEMPLATE
    assert "domain.scheduler" in SEED_TEMPLATE
```

- [ ] **Step 2: Run test to confirm it fails**

```bash
pytest features/feature_manager/tests/test_init_wizard.py::test_seed_template_includes_domain_experts -v
```

Expected: FAILED — `domain_experts` not in SEED_TEMPLATE yet.

- [ ] **Step 3: Update SEED_TEMPLATE in init_wizard.py**

In `features/feature_manager/init_wizard.py`, find the `SEED_TEMPLATE` string. After the `skills:` block (ending with `- skill.scribe-digest`), add:

```python
SEED_TEMPLATE = """# LMF Instance — Seed Profile (generated by init wizard)
# Replace remaining ((placeholders)) before deploying.

operator:
  name: "((OPERATOR_NAME))"
  email: "((OPERATOR_EMAIL))"
  phone: "((OPERATOR_PHONE))"

vault:
  root: "((VAULT_ROOT))"
  state_path: "((STATE_PATH))"

ntfy:
  url: "((NTFY_URL))"
  topic: "((NTFY_TOPIC))"

panels:
  - panel.marlin
  - panel.ai-chat
  - panel.ttf
  - panel.ink-blotter
  - panel.terminal
  - panel.vault
  - panel.projects
  - panel.quickhacks
  - panel.scribner

skills:
  - skill.marlin-capture
  - skill.marlin-enrich
  - skill.marlin-open
  - skill.marlin-close
  - skill.ttf-push
  - skill.marlin-learn
  - skill.project-reload
  - skill.scribe-digest

domain_experts:
  - domain.scheduler
  - domain.project-manager
  - domain.vault
  - domain.capture
  - domain.coach

endpoints:
  marlin: "((HOST_MARLIN))"
  ai_chat: "((HOST_AI_CHAT))"
  ttf: "((HOST_TTF))"
  ink_blotter: "((HOST_INK))"
  terminal: "((HOST_TERMINAL))"
  vault: "((HOST_VAULT))"
  projects: "((HOST_PROJECTS))"
  quickhacks: "((HOST_QUICKHACKS))"
  scribner: "((HOST_SCRIBNER))"
"""
```

- [ ] **Step 4: Add domain experts phase to run_wizard**

In `features/feature_manager/init_wizard.py`, find this exact block (around line 176):

```python
    print()
    print("--- Summary ---")
    summary = f"""  Operator: {name or '((OPERATOR_NAME))'}
  Email:    {email or '((OPERATOR_EMAIL))'}
  Phone:    {phone or '((OPERATOR_PHONE))'}
  Vault:    {vault_root or '((VAULT_ROOT))'}
  State:    {state_path or vault_root + '/../state.json'}
  Ntfy:     {'yes — ' + ntfy_url + '/' + ntfy_topic if use_ntfy else 'no'}
  Panels:   9 (default set)
  Skills:   10 (default set)"""
```

Replace it with:

```python
    print("--- Domain Experts ---")
    use_domain_experts = yes_no("Enable default domain experts?", default=True)
    print()
    print("--- Summary ---")
    summary = f"""  Operator: {name or '((OPERATOR_NAME))'}
  Email:    {email or '((OPERATOR_EMAIL))'}
  Phone:    {phone or '((OPERATOR_PHONE))'}
  Vault:    {vault_root or '((VAULT_ROOT))'}
  State:    {state_path or vault_root + '/../state.json'}
  Ntfy:     {'yes — ' + ntfy_url + '/' + ntfy_topic if use_ntfy else 'no'}
  Panels:   9 (default set)
  Skills:   8 (default set)
  Domain Experts: {'5 (default set)' if use_domain_experts else 'disabled'}"""
```

Find the profile construction block (around line 197) and replace it with:

```python
    profile = {
        "operator": {
            "name": name or "((OPERATOR_NAME))",
            "email": email or "((OPERATOR_EMAIL))",
            "phone": phone or "((OPERATOR_PHONE))",
        },
        "vault": {
            "root": vault_root or "((VAULT_ROOT))",
            "state_path": state_path or f"{vault_root}/../state.json",
        },
        "panels": [
            "panel.marlin", "panel.ai-chat", "panel.ttf",
            "panel.ink-blotter", "panel.terminal", "panel.vault",
            "panel.projects", "panel.quickhacks", "panel.scribner",
        ],
        "skills": [
            "skill.marlin-capture", "skill.marlin-enrich",
            "skill.marlin-open", "skill.marlin-close",
            "skill.ttf-push", "skill.marlin-learn",
            "skill.project-reload", "skill.scribe-digest",
        ],
        "endpoints": hosts,
    }
    if use_domain_experts:
        profile["domain_experts"] = [
            "domain.scheduler", "domain.project-manager",
            "domain.vault", "domain.capture", "domain.coach",
        ]
```

- [ ] **Step 5: Run all tests**

```bash
pytest features/feature_manager/tests/ -v
```

Expected: all tests PASS.

- [ ] **Step 6: Run full validation to confirm all registries pass**

```bash
cd /home/jared/Documents/Obsidian/Marlin
python3 -m features.feature_manager.manager validate
```

Expected output:
```
panels registry (...): all valid
skills registry (...): all valid
domain-experts registry (...): all valid

All manifests valid.
```

- [ ] **Step 7: Commit**

```bash
git add features/feature_manager/init_wizard.py features/feature_manager/tests/test_init_wizard.py
git commit -m "feat: add domain experts phase to init wizard and seed template"
```

---

## Done

All four tasks complete. The Feature Manager now:
- Accepts `domain-expert` as a valid manifest type with `classifier` and `context_template`
- Ships a `domain-experts/registry.json` with `domain.scheduler` as the first example
- Resolves `domain_experts` references in seed profiles
- Validates the domain experts registry in `cmd_validate`
- Prompts for domain experts in the init wizard

Next build (Option B): orchestrator routing module — reads installed domain experts, classifies messages, loads context, calls specialist.
