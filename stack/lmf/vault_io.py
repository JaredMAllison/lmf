from pathlib import Path
import re


class VaultIO:
    """File I/O layer for vault writes. Delegates all disk operations from Orchestrator._tool_* methods."""

    def __init__(self, root: str | Path):
        self.root = Path(root)

    def append_to_file(self, file_path: str, content: str) -> dict:
        target = self.root / file_path
        target.parent.mkdir(parents=True, exist_ok=True)
        current = target.read_text(encoding="utf-8").splitlines() if target.exists() else []
        new_lines = current + ["", content]
        target.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return {"file": file_path, "appended_at_line": len(new_lines)}

    def replace_lines(self, file_path: str, start_line: int, end_line: int, new_content: str) -> dict:
        target = self.root / file_path
        lines = target.read_text(encoding="utf-8").splitlines()
        start = max(1, start_line)
        end = min(len(lines), end_line)
        new_lines = lines[:start - 1] + new_content.splitlines() + lines[end:]
        target.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return {"file": file_path, "replaced_lines": end - start + 1, "new_line_count": len(new_lines)}

    def create_file(self, file_path: str, content: str) -> dict:
        target = self.root / file_path
        if target.exists():
            return {"error": f"file already exists: {file_path}"}
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {"file": file_path, "created": True, "line_count": len(content.splitlines())}

    def insert_after_heading(self, file_path: str, heading: str, content: str) -> dict:
        target = self.root / file_path
        lines = target.read_text(encoding="utf-8").splitlines()
        heading_lower = heading.lower()
        insert_at = None
        for i, line in enumerate(lines):
            if re.match(r'^#{1,6}\s+', line) and heading_lower in line.lower():
                insert_at = i + 1
                break
        if insert_at is None:
            return {"error": f"Heading '{heading}' not found in {file_path}"}
        new_lines = lines[:insert_at] + [""] + content.splitlines() + lines[insert_at:]
        target.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return {"file": file_path, "inserted_at_line": insert_at + 1}

    def list_files(self) -> list[dict]:
        files = []
        for fp in sorted(self.root.rglob("*.md")):
            rel = fp.relative_to(self.root).as_posix()
            lines = fp.read_text(encoding="utf-8").splitlines()
            size_kb = round(fp.stat().st_size / 1024, 1)
            files.append({"file": rel, "line_count": len(lines), "size_kb": size_kb})
        return files
