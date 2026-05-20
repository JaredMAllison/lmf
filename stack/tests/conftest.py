"""Test fixtures for LMF stack modules.

Creates a temporary vault directory with realistic sample content
for testing build_prompt.py, vault_io.py, and related modules.
"""

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def sample_vault():
    """Create a temporary vault with sample files for prompt building tests.

    Structure:
      vault/
        System/Memory/ARIEL.md          — identity doc
        System/Memory/MEMORY.md          — memory index
        System/Memory/memory-core.md     — core memory (loaded by default)
        System/Memory/memory-extended.md — extended memory (not loaded)
        System/Stack/stack.md            — stack config + skill allowlist
        System/Skills/marlin-capture/SKILL.md
        System/Skills/ttf-push/SKILL.md
        Tasks/task-one.md
        Inbox.md
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        vault = Path(tmpdir)

        # -- System/Memory/ARIEL.md --
        memory_dir = vault / "System" / "Memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "ARIEL.md").write_text(
            "name: Ariel\nrole: Vault Assistant\ninstance: Marlin\n"
            "You are Ariel, a personal vault assistant."
        )

        # -- System/Memory/MEMORY.md --
        (memory_dir / "MEMORY.md").write_text(
            "- (memory-core.md)\n"
            "- (memory-extended.md) — tier: extended\n"
        )

        # -- System/Memory/memory-core.md --
        (memory_dir / "memory-core.md").write_text(
            "---\ntier: core\n---\n# Core Memory\n\nOperator prefers direct communication."
        )

        # -- System/Memory/memory-extended.md --
        (memory_dir / "memory-extended.md").write_text(
            "---\ntier: extended\n---\n# Extended Memory\n\nOptional context."
        )

        # -- System/Stack/stack.md --
        stack_dir = vault / "System" / "Stack"
        stack_dir.mkdir(parents=True)
        (stack_dir / "stack.md").write_text(
            "ai_name: Ariel\n"
            "skill_allowlist:\n"
            "  - marlin-capture\n"
        )

        # -- System/Skills -- one with allowlist match, one without
        skills_dir = vault / "System" / "Skills"
        capture_dir = skills_dir / "marlin-capture"
        capture_dir.mkdir(parents=True)
        (capture_dir / "SKILL.md").write_text(
            "---\nname: marlin-capture\ndescription: Fast task capture\n---\n"
            "# Capture\n\nUse for quick inbox writes."
        )
        ttf_dir = skills_dir / "ttf-push"
        ttf_dir.mkdir(parents=True)
        (ttf_dir / "SKILL.md").write_text(
            "---\nname: ttf-push\ndescription: Push tasks to TTF\n---\n"
            "# TTF Push\n\nPushes tasks to Time Factory."
        )

        # -- Extra vault files (should not affect prompt) --
        (vault / "Tasks").mkdir()
        (vault / "Tasks" / "task-one.md").write_text("---\ntitle: Test task\n---\n")
        (vault / "Inbox.md").write_text("")

        yield vault


@pytest.fixture
def sample_vault_no_stack(sample_vault):
    """A vault with no System/Stack/stack.md — tests fallback behavior."""
    stack_file = sample_vault / "System" / "Stack" / "stack.md"
    stack_file.unlink()
    return sample_vault


@pytest.fixture
def sample_vault_no_identity(sample_vault):
    """A vault with no ARIEL.md — tests fallback behavior."""
    identity_file = sample_vault / "System" / "Memory" / "ARIEL.md"
    identity_file.unlink()
    return sample_vault


@pytest.fixture
def sample_vault_no_skills(sample_vault):
    """A vault with no System/Skills/ — tests empty skill index."""
    skills_dir = sample_vault / "System" / "Skills"
    import shutil
    shutil.rmtree(skills_dir)
    return sample_vault
