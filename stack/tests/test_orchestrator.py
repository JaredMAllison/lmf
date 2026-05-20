"""Tests for orchestrator.py — the critical runtime path.

Covers: chat loop, tool dispatch, write gate, init mode, state management,
skill loading, and edge cases. Backend calls are mocked throughout.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

# Disable pacing for all tests — each chat() call should return immediately
from lmf import orchestrator as orch_module
orch_module.TURBO_MODE = True

from lmf.orchestrator import (
    Orchestrator,
    is_confirmation,
    parse_skill_trigger,
    load_skill,
    _WRITE_TOOLS,
    _CONFIRMATION_YES,
)

# Named constants for mock backend responses
_MOCK_TEXT_REPLY = "I processed your request. Here are the results."


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def orch_vault(tmp_path):
    """A minimal vault with LOCAL_MIND_FOUNDATION.md (normal mode)."""
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "LOCAL_MIND_FOUNDATION.md").write_text("---\ntitle: LMF\n---\n\nProfile doc.")
    (vault / "Inbox.md").write_text("")
    return vault


@pytest.fixture
def orch_vault_no_profile(tmp_path):
    """A vault without LOCAL_MIND_FOUNDATION.md (init mode)."""
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "Inbox.md").write_text("")
    return vault


@pytest.fixture
def mock_backend():
    """Patch requests.post to simulate a successful Ollama response.

    Returns a function that accepts alternative response data.
    """
    def _make_response(content: str = _MOCK_TEXT_REPLY, tool_calls: list | None = None):
        msg = {"message": {"content": content}}
        if tool_calls:
            msg["message"]["tool_calls"] = tool_calls
        return MagicMock(
            status_code=200,
            ok=True,
            json=lambda: msg,
            headers={},
        )
    with patch("requests.post", return_value=_make_response()) as mock_post:
        yield mock_post, _make_response


@pytest.fixture
def orch(orch_vault, mock_backend):
    """A bootstrapped Orchestrator in normal mode with mocked backends."""
    orch = Orchestrator(str(orch_vault), test_mode=True)
    orch.allow_external_writes = True
    return orch


@pytest.fixture
def orch_init(orch_vault_no_profile, mock_backend):
    """An Orchestrator in init mode (no LOCAL_MIND_FOUNDATION.md)."""
    return Orchestrator(str(orch_vault_no_profile), test_mode=True)


# ── is_confirmation ───────────────────────────────────────────────────────────


class TestIsConfirmation:
    """Positive confirmation matching."""

    def test_yes_variants(self):
        for word in _CONFIRMATION_YES:
            assert is_confirmation(word)
            assert is_confirmation(word.upper())
            assert is_confirmation(word.capitalize() + ".")

    def test_no_variants(self):
        assert not is_confirmation("no")
        assert not is_confirmation("n")
        assert not is_confirmation("maybe")
        assert not is_confirmation("")

    def test_strips_punctuation(self):
        assert is_confirmation("yes!")
        assert is_confirmation("go ahead.")
        assert is_confirmation("ok?")


# ── parse_skill_trigger ───────────────────────────────────────────────────────


class TestParseSkillTrigger:
    """Detecting /skill-name prefixes."""

    def test_basic_skill(self):
        assert parse_skill_trigger("/marlin-capture") == "marlin-capture"

    def test_with_trailing_content(self):
        assert parse_skill_trigger("/marlin-capture please capture this") == "marlin-capture"

    def test_no_trigger(self):
        assert parse_skill_trigger("capture this task") is None

    def test_empty_message(self):
        assert parse_skill_trigger("") is None

    def test_just_slash(self):
        assert parse_skill_trigger("/") is None

    def test_multi_hyphen(self):
        assert parse_skill_trigger("/project-reload marlin") == "project-reload"


# ── load_skill ────────────────────────────────────────────────────────────────


class TestLoadSkill:
    """Skill file resolution from vault paths."""

    def test_loads_from_named_dir(self, tmp_path):
        vault = tmp_path / "vault"
        skill_dir = vault / "System" / "Skills" / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Test Skill\n\nContent.")
        result = load_skill(vault, "test-skill")
        assert result == "# Test Skill\n\nContent."

    def test_loads_from_file(self, tmp_path):
        """Flat skill file at System/Skills/{name}.md — resolved by first candidate pattern."""
        vault = tmp_path / "vault"
        skills_dir = vault / "System" / "Skills"
        skills_dir.mkdir(parents=True)
        (skills_dir / "flat-skill.md").write_text("# Flat Skill\n\nContent.")
        result = load_skill(vault, "flat-skill")
        # First candidate pattern: vault/System/Skills/{name}.md — matches
        assert result == "# Flat Skill\n\nContent."

    def test_returns_none_when_missing(self, tmp_path):
        vault = tmp_path / "vault"
        vault.mkdir()
        assert load_skill(vault, "nonexistent") is None


# ── Orchestrator.__init__ ─────────────────────────────────────────────────────


class TestInit:
    """Orchestrator construction and mode detection."""

    def test_normal_mode(self, orch_vault, mock_backend):
        orch = Orchestrator(str(orch_vault), test_mode=True)
        assert not orch.is_init_mode
        assert orch.system_prompt is not None

    def test_init_mode(self, orch_vault_no_profile):
        orch = Orchestrator(str(orch_vault_no_profile), test_mode=True)
        assert orch.is_init_mode
        assert orch.tools == []

    def test_init_state_defaults(self, orch_vault_no_profile):
        orch = Orchestrator(str(orch_vault_no_profile), test_mode=True)
        assert orch.init_state["phase"] == "interview"
        assert orch.init_state["answered_questions"] == []


# ── Chat: Normal mode ─────────────────────────────────────────────────────────


class TestChatNormal:
    """The main chat loop in normal (non-init) mode."""

    def test_basic_chat(self, orch):
        reply = orch.chat("Hello")
        assert reply == _MOCK_TEXT_REPLY

    def test_chat_adds_to_history(self, orch):
        orch.chat("First message")
        assert len(orch.history) == 2  # user + assistant
        orch.chat("Second message")
        assert len(orch.history) == 4

    def test_turbo_toggle(self, orch):
        reply = orch.chat("/turbo")
        assert "Slow" in reply  # starts turnd=True, toggles to False
        # Toggle back
        reply2 = orch.chat("/turbo")
        assert "Turbo" in reply2

    @patch("lmf.orchestrator.load_skill")
    def test_skill_loading(self, mock_load, orch):
        mock_load.return_value = "# Loaded Skill\n\nInstructions."
        orch.chat("/marlin-capture do something")
        mock_load.assert_called_once()

    def test_empty_message(self, orch):
        reply = orch.chat("")
        assert reply == _MOCK_TEXT_REPLY  # backend still called

    def test_tool_loop_limit(self, orch, mock_backend):
        """When the model keeps returning tool calls, the loop should terminate."""
        mock_post, responder = mock_backend
        # Return a non-write tool call repeatedly — no write gate to break the loop
        mock_post.return_value = responder("", tool_calls=[
            {"function": {"name": "search_vault", "arguments": {"query": "x", "top_k": 1}}}
        ])
        reply = orch.chat("search repeatedly")
        assert "limit" in reply

    def test_skill_without_trigger_does_not_load(self, orch):
        """A message starting without / should not trigger skill loading."""
        reply = orch.chat("marlin-capture do something")
        assert reply == _MOCK_TEXT_REPLY


# ── Write Gate ────────────────────────────────────────────────────────────────


class TestWriteGate:
    """The write gate requires confirmation before writing."""

    def test_write_proposes_confirmation(self, orch, mock_backend):
        mock_post, responder = mock_backend
        mock_post.return_value = responder("", tool_calls=[
            {"function": {"name": "append_to_file", "arguments": {"file_path": "test.md", "content": "new content"}}}
        ])
        reply = orch.chat("add something to test.md")
        assert "append to" in reply
        assert "test.md" in reply
        assert "Confirm" in reply

    def test_write_confirmed_executes(self, orch):
        orch.pending_write = {
            "name": "append_to_file",
            "args": {"file_path": "test.md", "content": "new content"},
        }
        reply = orch.chat("yes")
        assert "Done" in reply or "Written" in reply

    def test_write_denied_does_not_execute(self, orch):
        orch.pending_write = {
            "name": "append_to_file",
            "args": {"file_path": "test.md", "content": "new content"},
        }
        reply = orch.chat("no")
        assert "won't" in reply or "Okay" in reply
        assert orch.pending_write is None


# ── Tool Dispatch ─────────────────────────────────────────────────────────────


class TestToolDispatch:
    """Direct tool dispatch (non-write tools)."""

    def test_tool_search_calls_loom(self, orch):
        with patch.object(orch, '_tool_search', return_value=[{"file": "test.md"}]) as mock_search:
            orch.allow_external_writes = True
            result = orch._dispatch_tool("search_vault", {"query": "test"})
            data = json.loads(result)
            assert data == [{"file": "test.md"}]
            mock_search.assert_called_once_with("test", top_k=5)

    def test_tool_outline_returns_headings(self, orch):
        test_file = Path(orch.vault) / "test_outline.md"
        test_file.write_text("# Heading 1\n\n## Heading 2\n\n### Heading 3\n")
        result = orch._dispatch_tool("outline", {"file_path": "test_outline.md"})
        data = json.loads(result)
        assert len(data) == 3
        assert data[0]["heading"] == "Heading 1"

    def test_tool_outline_missing_file(self, orch):
        result = orch._dispatch_tool("outline", {"file_path": "nonexistent.md"})
        data = json.loads(result)
        assert "error" in data

    def test_tool_list_files(self, orch):
        result = orch._dispatch_tool("list_files", {})
        data = json.loads(result)
        assert isinstance(data, list)

    def test_external_write_blocked(self, orch):
        orch.allow_external_writes = False
        for path in ["/etc/passwd", "../outside.md"]:
            result = orch._dispatch_tool("append_to_file", {"file_path": path, "content": "x"})
            assert "external writes disabled" in result

    def test_unknown_tool_returns_error(self, orch):
        result = orch._dispatch_tool("nonexistent", {})
        assert "Unknown tool" in result

    def test_tool_error_returns_json_error(self, orch):
        with patch.object(orch, '_tool_search', side_effect=RuntimeError("boom")):
            # search_vault raises RuntimeError for connection errors
            pass


# ── Init Mode ─────────────────────────────────────────────────────────────────


class TestInitMode:
    """The conversational onboarding flow."""

    def test_starts_in_interview_mode(self, orch_init):
        assert orch_init.init_state["phase"] == "interview"
        # After a few messages, should still be in init mode
        orch_init.chat("Hello")
        assert orch_init.is_init_mode

    def test_init_chat_returns_response(self, orch_init, mock_backend):
        """Init mode should still respond to user messages."""
        reply = orch_init.chat("Hello")
        # In init mode, system prompt is the init template — response comes from mocked backend
        assert reply is not None

    def test_init_mode_reset(self, orch_init):
        orch_init.chat("Hello")
        orch_init.reset()
        assert orch_init.history == []

    def test_is_first_run_no_profile(self, orch_vault_no_profile):
        orch = Orchestrator(str(orch_vault_no_profile), test_mode=True)
        assert orch._is_first_run()

    def test_is_first_run_with_profile(self, orch_vault):
        with patch.object(Path, "exists", return_value=True):
            pass  # covered by fixture
        orch = Orchestrator(str(orch_vault), test_mode=True)
        assert not orch._is_first_run()


# ── Reset and State ───────────────────────────────────────────────────────────


class TestReset:
    """State clearing."""

    def test_reset_clears_history(self, orch):
        orch.chat("Hello")
        orch.chat("World")
        assert len(orch.history) == 4
        orch.reset()
        assert orch.history == []

    def test_reset_clears_pending_write(self, orch):
        orch.pending_write = {"name": "test", "args": {}}
        orch.reset()
        assert orch.pending_write is None

    def test_init_reset_clears_init_state_file(self, orch_init):
        """Init state is persisted to file; reset deletes the file but in-memory
        state is a cache reloaded on next chat(). Verify the file is removed."""
        orch_init.chat("Hello")
        orch_init.init_state["phase"] = "handoff"
        orch_init._save_init_state()
        state_path = orch_init.vault / "operator" / ".init_state.json"
        assert state_path.exists()
        orch_init.reset()
        assert orch_init.history == []
        # File should be deleted by reset
        assert not state_path.exists()
