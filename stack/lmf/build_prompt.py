"""
build_prompt.py — Ariel system prompt compiler.

Assembles a complete system prompt from:
  1. Identity doc (System/Memory/ARIEL.md)
  2. All memory files listed in System/Memory/MEMORY.md
  3. Skill index (name + description from each System/Skills/*/SKILL.md)

Stack-level: parameterized by vault path. Works for any LMF vault instance.
Each vault supplies its own ARIEL.md + System/Memory/ + System/Skills/.

Usage:
  python3 build_prompt.py [vault_path]     # prints compiled prompt to stdout
  from build_prompt import build_prompt    # returns string
"""

import re
import sys
from pathlib import Path

IDENTITY_PATH = "System/Memory/ARIEL.md"
STACK_PATH    = "System/Stack/stack.md"
MEMORY_INDEX  = "System/Memory/MEMORY.md"
SKILLS_DIR    = "System/Skills"


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _parse_memory_files(index_path: Path, tier: str = "core") -> list[Path]:
    """Parse MEMORY.md and return paths of memory files matching the given tier.

    Files with no tier field are treated as core (backwards compatible).
    """
    if not index_path.exists():
        return []
    files = []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        match = re.search(r"\(([^)]+\.md)\)", line)
        if not match:
            continue
        path = index_path.parent / match.group(1)
        if not path.exists():
            continue
        file_tier = _parse_frontmatter_field(path.read_text(encoding="utf-8"), "tier")
        if not file_tier or file_tier == tier:
            files.append(path)
    return files


def _parse_frontmatter_list(text: str, field: str) -> list[str]:
    """Extract a YAML block list from frontmatter (- item per line format)."""
    block_match = re.search(
        rf'^{field}:\s*\n((?:[ \t]+-[ \t]+\S+\n?)+)',
        text, re.MULTILINE
    )
    if not block_match:
        return []
    items = []
    for line in block_match.group(1).splitlines():
        item = re.sub(r'^[ \t]+-[ \t]+', '', line).strip()
        if item:
            items.append(item)
    return items


def _parse_frontmatter_field(text: str, field: str) -> str:
    """Extract a single field value from YAML frontmatter.

    Handles inline values and block scalars (|, >, |-) by returning
    the first non-empty content line for block types.
    """
    match = re.search(rf'^{field}:[ \t]*(.*?)$', text, re.MULTILINE)
    if not match:
        return ""
    value = match.group(1).strip().strip('"')
    # Block scalar marker — find the first non-empty indented line that follows
    if value in ("|", ">", "|-", ">-"):
        block_match = re.search(
            rf'^{field}:\s*[|>-]+\n((?:[ \t]+.+\n?)+)',
            text,
            re.MULTILINE,
        )
        if block_match:
            for line in block_match.group(1).splitlines():
                stripped = line.strip()
                if stripped:
                    return stripped
        return ""
    return value


def _build_skill_index(vault: Path, allowlist: list[str] | None = None) -> tuple[str, int]:
    """Scan System/Skills/ and return (index_text, count).

    If allowlist is provided, only skills whose name appears in it are included.
    """
    skills_dir = vault / SKILLS_DIR
    if not skills_dir.exists():
        return "", 0

    entries = []
    for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
        text = skill_file.read_text(encoding="utf-8")
        name = _parse_frontmatter_field(text, "name")
        if not name:
            continue
        if allowlist is not None and name not in allowlist:
            continue
        description = _parse_frontmatter_field(text, "description")
        if description:
            entries.append(f"- /{name}: {description}")

    return "\n".join(entries), len(entries)


def build_manifest(awareness: dict, turn_number: int = 0,
                   session_summaries: list[str] | None = None,
                   show_meter: bool = True,
                   knowledge_domains: list[dict] | None = None) -> str:
    """Build per-turn manifest section from the awareness tracker state.

    `awareness` shape:
    {
        "pinned": {"path/to/file.md": {"last_turn": 0, "access_count": 1}, ...},
        "active": {"path/to/file.md": {"last_turn": 3, "access_count": 2}, ...},
        "stale":  {"path/to/file.md": {"last_turn": 10, "access_count": 1, "eviction_in": 2}, ...},
        "dismissed": {"path/to/file.md": {"last_turn": 5, "access_count": 0, "revived": False}, ...},
        "budget_remaining": 4096,
        "budget_total": 8192,
    }

    `session_summaries`: previous turn summaries for conversational awareness.
    `show_meter`: render the ASCII budget meter bar.

    Returns a formatted markdown block.
    """
    sections = ["## Current Awareness (Manifest)"]

    def _fmt_section(label: str, icon: str, files: dict, show_eviction: bool = False):
        if not files:
            return ""
        lines = [f"\n### {icon} {label}"]
        for path, info in sorted(files.items(), key=lambda x: x[1].get("last_turn", 0)):
            parts = [f"- {path}"]
            parts.append(f"  last turn: {info.get('last_turn', '?')}")
            if show_eviction and "eviction_in" in info:
                parts.append(f"  evict in ~{info['eviction_in']} turns")
            if info.get("revived"):
                parts.append("  (revived this turn)")
            lines.append("\n".join(parts))
        return "\n".join(lines)

    pinned_s = _fmt_section("Pinned", "📌", awareness.get("pinned", {}))
    active_s = _fmt_section("Active", "📄", awareness.get("active", {}))
    stale_s  = _fmt_section("Stale", "⏳", awareness.get("stale", {}), show_eviction=True)
    dismissed_s = _fmt_section("Dismissed", "👻", awareness.get("dismissed", {}))

    for block in (pinned_s, active_s, stale_s, dismissed_s):
        if block:
            sections.append(block)

    # Knowledge domains — background corpora, searchable on request
    if knowledge_domains:
        dome_lines = ["\n### Knowledge Domains (search on request)"]
        for d in knowledge_domains:
            path = d.get("path", "")
            desc = d.get("description", "")
            dome_lines.append(f"- {path} — {desc}")
        sections.append("\n".join(dome_lines))

    # Session memory — last N turn summaries
    if session_summaries:
        summary_lines = ["\n### Session Memory"]
        for i, s in enumerate(session_summaries, 1):
            summary_lines.append(f"{i}. {s}")
        sections.append("\n".join(summary_lines))

    # Meter
    if show_meter:
        meter = awareness.get("budget_remaining", 0)
        total = awareness.get("budget_total", 8192)
        pct = int((1 - meter / total) * 100) if total else 0
        bar_len = 20
        filled = int(bar_len * pct / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        sections.append(f"\n### Meter\n`{bar}` {pct}% used — {meter} / {total} tokens remaining")

    return "\n".join(sections) + "\n"


def build_prompt(vault_path: str | Path) -> tuple[str, dict]:
    """Return (prompt_text, stats) where stats has memory_files_loaded and skills_in_index."""
    vault = Path(vault_path)
    sections = []

    # 1 — Identity
    identity = _read(vault / IDENTITY_PATH)
    if identity:
        sections.append("# Identity\n\n" + identity)
    else:
        sections.append(
            "# Identity\n\n"
            f"[{IDENTITY_PATH} not found in vault at {vault}. "
            "Operating without identity context until ARIEL.md is created.]"
        )

    # 2 — Stack spec
    stack = _read(vault / STACK_PATH)
    skill_allowlist = _parse_frontmatter_list(stack, "skill_allowlist") if stack else None
    if stack:
        sections.append("# Stack\n\n" + stack)

    # 3 — Memory
    memory_files = _parse_memory_files(vault / MEMORY_INDEX)
    blocks = []
    for path in memory_files:
        # Skip ARIEL.md if it appears in the index — already loaded as identity
        if path.name == "ARIEL.md":
            continue
        content = _read(path)
        if content:
            blocks.append(f"### {path.stem}\n\n{content}")

    memory_count = len(blocks)
    if blocks:
        sections.append("# Memory\n\n" + "\n\n---\n\n".join(blocks))

    # 4 — Skill index
    skill_index, skill_count = _build_skill_index(vault, allowlist=skill_allowlist or None)
    if skill_index:
        sections.append(
            "# Skills\n\n"
            "Invoke a skill by starting your message with /skill-name. "
            "The full skill will be loaded and its instructions followed.\n\n"
            + skill_index
        )

    # 5 — Tool use rules (always appended, not vault-content-dependent)
    sections.append(
        "# Tool Use Rules\n\n"
        "1. After calling a tool, always synthesize the results into a natural "
        "language response. Do not output raw tool JSON.\n"
        "2. If a tool returns zero results, an error, or a file-not-found, "
        "say so directly. Do not fabricate answers from empty results.\n"
        "3. If you are uncertain whether information exists in the vault, "
        "search first. If search returns nothing, say you couldn't find it "
        "rather than making something up.\n"
        "4. The append_to_file and replace_lines tools require user "
        "confirmation before executing. Propose the change and wait.\n"
    )

    prompt = "\n\n---\n\n".join(sections)
    stats = {"memory_files_loaded": memory_count, "skills_in_index": skill_count}
    return prompt, stats


if __name__ == "__main__":
    vault = sys.argv[1] if len(sys.argv) > 1 else str(Path.home() / "Documents" / "vault")
    prompt, stats = build_prompt(vault)
    print(prompt)
    print(f"\n[stats: {stats}]", file=__import__("sys").stderr)
