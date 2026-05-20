"""Tests for build_prompt.py — system prompt assembly from vault components.

Critical path tests for the prompt compiler, which is the entry point
for all assistant behavior. Tests cover frontmatter parsing, memory
index resolution, skill allowlisting, and full prompt assembly.
"""

from pathlib import Path

import pytest

from lmf.build_prompt import (
    _parse_frontmatter_field,
    _parse_frontmatter_list,
    _parse_memory_files,
    _build_skill_index,
    build_prompt,
)


# ── _parse_frontmatter_field ──────────────────────────────────────────────────


class TestParseFrontmatterField:
    """Extracting single values from YAML frontmatter."""

    def test_inline_value(self):
        text = "---\nname: Ariel\nrole: assistant\n---\n\nBody"
        assert _parse_frontmatter_field(text, "name") == "Ariel"
        assert _parse_frontmatter_field(text, "role") == "assistant"

    def test_block_scalar(self):
        text = "---\ndescription: |\n  Multi-line\n  description here\n---\n"
        assert _parse_frontmatter_field(text, "description") == "Multi-line"

    def test_folded_scalar(self):
        text = "---\nsummary: >\n  Folded text\n  into one line\n---\n"
        assert _parse_frontmatter_field(text, "summary") == "Folded text"

    def test_quoted_value(self):
        text = '---\ntitle: "Hello World"\n---\n'
        assert _parse_frontmatter_field(text, "title") == "Hello World"

    def test_missing_field(self):
        text = "---\nname: Ariel\n---\n"
        assert _parse_frontmatter_field(text, "nonexistent") == ""

    def test_no_frontmatter(self):
        text = "# Just Content\n\nNo frontmatter here."
        assert _parse_frontmatter_field(text, "name") == ""

    def test_empty_value(self):
        text = "---\nname:\n---\n"
        assert _parse_frontmatter_field(text, "name") == ""

    def test_field_after_frontmatter_only_matches_header(self):
        """A field appearing in the body should not be extracted."""
        text = "---\nname: Ariel\n---\n\nname: Not a frontmatter field"
        assert _parse_frontmatter_field(text, "name") == "Ariel"


# ── _parse_frontmatter_list ───────────────────────────────────────────────────


class TestParseFrontmatterList:
    """Extracting list values from YAML frontmatter."""

    def test_basic_list(self):
        text = "---\ntags:\n  - adr\n  - lmf\n  - architecture\n---\n"
        assert _parse_frontmatter_list(text, "tags") == ["adr", "lmf", "architecture"]

    def test_single_item(self):
        text = "---\nallowlist:\n  - marlin-capture\n---\n"
        assert _parse_frontmatter_list(text, "allowlist") == ["marlin-capture"]

    def test_empty_list(self):
        text = "---\nitems:\n---\n"
        assert _parse_frontmatter_list(text, "items") == []

    def test_no_frontmatter(self):
        assert _parse_frontmatter_list("# No frontmatter", "tags") == []

    def test_missing_field(self):
        text = "---\nname: Ariel\n---\n"
        assert _parse_frontmatter_list(text, "tags") == []


# ── _parse_memory_files ───────────────────────────────────────────────────────


class TestParseMemoryFiles:
    """Resolving memory file paths from MEMORY.md index."""

    def test_returns_core_memory_files(self, sample_vault):
        index_path = sample_vault / "System" / "Memory" / "MEMORY.md"
        files = _parse_memory_files(index_path, tier="core")
        names = [f.name for f in files]
        assert "memory-core.md" in names
        assert "memory-extended.md" not in names  # tier: extended

    def test_returns_extended_when_requested(self, sample_vault):
        index_path = sample_vault / "System" / "Memory" / "MEMORY.md"
        files = _parse_memory_files(index_path, tier="extended")
        names = [f.name for f in files]
        assert "memory-extended.md" in names
        assert "memory-core.md" not in names

    def test_empty_when_index_missing(self, sample_vault):
        missing = sample_vault / "System" / "Memory" / "NOEXIST.md"
        assert _parse_memory_files(missing) == []

    def test_skips_missing_files_gracefully(self, sample_vault):
        index_path = sample_vault / "System" / "Memory" / "MEMORY.md"
        # Add a reference to a file that doesn't exist
        with open(index_path, "a") as f:
            f.write("- [[ghost.md]]\n")
        files = _parse_memory_files(index_path)
        assert all(f.exists() for f in files)


# ── _build_skill_index ────────────────────────────────────────────────────────


class TestBuildSkillIndex:
    """Building skill index text from System/Skills/."""

    def test_all_skills_returned_with_no_allowlist(self, sample_vault):
        text, count = _build_skill_index(sample_vault)
        assert count == 2  # marlin-capture, ttf-push
        assert "/marlin-capture" in text
        assert "/ttf-push" in text

    def test_allowlist_filters_skills(self, sample_vault):
        text, count = _build_skill_index(sample_vault, allowlist=["marlin-capture"])
        assert count == 1
        assert "/marlin-capture" in text
        assert "/ttf-push" not in text

    def test_empty_allowlist_returns_nothing(self, sample_vault):
        text, count = _build_skill_index(sample_vault, allowlist=[])
        assert count == 0
        assert text == ""

    def test_no_skills_dir(self, sample_vault_no_skills):
        text, count = _build_skill_index(sample_vault_no_skills)
        assert count == 0
        assert text == ""

    def test_skill_without_name_is_skipped(self, sample_vault):
        """A SKILL.md with no frontmatter name should not appear."""
        no_name_dir = sample_vault / "System" / "Skills" / "unnamed"
        no_name_dir.mkdir()
        (no_name_dir / "SKILL.md").write_text("# Unnamed\n\nNo frontmatter.")
        text, count = _build_skill_index(sample_vault)
        assert count == 2  # still only the two named skills


# ── build_prompt ──────────────────────────────────────────────────────────────


class TestBuildPrompt:
    """Full prompt assembly — the main entry point."""

    def test_returns_prompt_and_stats(self, sample_vault):
        prompt, stats = build_prompt(str(sample_vault))
        assert isinstance(prompt, str)
        assert stats["memory_files_loaded"] == 1  # core only
        assert stats["skills_in_index"] == 1  # allowlist filters to marlin-capture

    def test_includes_identity(self, sample_vault):
        prompt, _ = build_prompt(str(sample_vault))
        assert "# Identity" in prompt
        assert "Ariel" in prompt

    def test_includes_stack_section(self, sample_vault):
        prompt, _ = build_prompt(str(sample_vault))
        assert "# Stack" in prompt
        assert "skill_allowlist" in prompt

    def test_applies_skill_allowlist(self, sample_vault):
        prompt, stats = build_prompt(str(sample_vault))
        assert stats["skills_in_index"] == 1  # only marlin-capture allowed
        assert "/marlin-capture" in prompt
        assert "/ttf-push" not in prompt

    def test_includes_memory_section(self, sample_vault):
        prompt, _ = build_prompt(str(sample_vault))
        assert "# Memory" in prompt
        assert "Core Memory" in prompt
        assert "Operator prefers direct communication" in prompt

    def test_does_not_repeat_identity_in_memory(self, sample_vault):
        """ARIEL.md should appear as identity, not duplicated in memory section."""
        prompt, _ = build_prompt(str(sample_vault))
        id_pos = prompt.index("# Identity")
        mem_pos = prompt.index("# Memory")
        assert id_pos < mem_pos  # identity comes first

    def test_includes_tool_use_rules(self, sample_vault):
        prompt, _ = build_prompt(str(sample_vault))
        assert "# Tool Use Rules" in prompt
        assert "synthesize the results" in prompt

    def test_fallback_without_stack(self, sample_vault_no_stack):
        """Without stack.md, all skills are available."""
        prompt, stats = build_prompt(str(sample_vault_no_stack))
        assert stats["skills_in_index"] == 2  # no allowlist, both skills included
        assert "/marlin-capture" in prompt
        assert "/ttf-push" in prompt

    def test_fallback_without_identity(self, sample_vault_no_identity):
        """Without ARIEL.md, identity section shows a not-found message."""
        prompt, _ = build_prompt(str(sample_vault_no_identity))
        assert "# Identity" in prompt
        assert "not found" in prompt.lower()

    def test_no_skills_dir(self, sample_vault_no_skills):
        """Without skills, prompt has no skill index."""
        prompt, stats = build_prompt(str(sample_vault_no_skills))
        assert stats["skills_in_index"] == 0
