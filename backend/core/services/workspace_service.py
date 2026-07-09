from __future__ import annotations

import json
import shutil
import socket
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from ..config import PROJECT_ROOT


RUNTIME_DIR = PROJECT_ROOT / "runtime"
WORKSPACES_DIR = RUNTIME_DIR / "workspaces"
QUEUE_FILE = RUNTIME_DIR / "task_queue.json"
DEFAULT_EXCLUDES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".next",
    ".agent-intake",
    "__pycache__",
    "fabrika_Agent",
}
SOURCE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".java": "java",
    ".rs": "rust",
    ".cs": "csharp",
    ".php": "php",
    ".rb": "ruby",
    ".sql": "sql",
}
DB_PATTERNS = {
    "postgresql": ("postgres", "asyncpg", "psycopg", "postgresql"),
    "mongodb": ("mongodb", "mongoose", "motor", "pymongo"),
    "redis": ("redis", "ioredis", "redis://"),
    "sqlite": ("sqlite", "aiosqlite", "sqlite3"),
}


@dataclass
class WorkspaceTask:
    id: str
    source_path: str
    workspace_path: str
    prompt: str
    requires_internet: bool
    status: str
    created_at: str
    updated_at: str
    retry_count: int = 0
    last_error: str | None = None
    report_path: str | None = None


class WorkspaceService:
    def __init__(self) -> None:
        self._lock = Lock()
        RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
        WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)
        if not QUEUE_FILE.exists():
            QUEUE_FILE.write_text("[]", encoding="utf-8")

    def list_tasks(self) -> list[WorkspaceTask]:
        return self._load_tasks()

    def get_task(self, task_id: str) -> WorkspaceTask | None:
        for task in self._load_tasks():
            if task.id == task_id:
                return task
        return None

    def enqueue_or_run(self, source_path: str, prompt: str, requires_internet: bool) -> WorkspaceTask:
        source = Path(source_path).expanduser().resolve()
        if not source.exists() or not source.is_dir():
            raise ValueError("Source path must be an existing directory")

        workspace_name = f"{source.name}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}"
        workspace_path = WORKSPACES_DIR / workspace_name
        now = datetime.now(timezone.utc).isoformat()
        task = WorkspaceTask(
            id=str(uuid4()),
            source_path=str(source),
            workspace_path=str(workspace_path),
            prompt=prompt,
            requires_internet=requires_internet,
            status="pending",
            created_at=now,
            updated_at=now,
        )

        tasks = self._load_tasks()
        tasks.append(task)
        self._save_tasks(tasks)

        if not requires_internet or self._has_internet():
            return self.process_task(task.id)
        return task

    def process_pending(self) -> list[WorkspaceTask]:
        tasks = self._load_tasks()
        processed: list[WorkspaceTask] = []
        for task in tasks:
            if task.status != "pending":
                continue
            if task.requires_internet and not self._has_internet():
                continue
            processed.append(self.process_task(task.id))
        return processed

    def process_task(self, task_id: str) -> WorkspaceTask:
        with self._lock:
            tasks = self._load_tasks()
            task = next((item for item in tasks if item.id == task_id), None)
            if task is None:
                raise ValueError("Task not found")

            task.status = "processing"
            task.updated_at = datetime.now(timezone.utc).isoformat()
            self._save_tasks(tasks)

            try:
                report_path = self._run_intake(task)
                task.status = "completed"
                task.report_path = str(report_path)
                task.last_error = None
            except OSError as exc:
                task.retry_count += 1
                task.last_error = str(exc)
                task.status = "pending" if task.requires_internet else "failed"
            except Exception as exc:
                task.retry_count += 1
                task.last_error = str(exc)
                task.status = "failed"

            task.updated_at = datetime.now(timezone.utc).isoformat()
            self._save_tasks(tasks)
            return task

    def _run_intake(self, task: WorkspaceTask) -> Path:
        source = Path(task.source_path)
        workspace = Path(task.workspace_path)
        if not workspace.exists():
            shutil.copytree(source, workspace, ignore=shutil.ignore_patterns(*DEFAULT_EXCLUDES))

        output_dir = workspace / ".agent-intake"
        output_dir.mkdir(parents=True, exist_ok=True)

        all_files = [
            path
            for path in workspace.rglob("*")
            if path.is_file() and not any(part in DEFAULT_EXCLUDES for part in path.parts)
        ]

        language_counts: dict[str, int] = {}
        db_hits: set[str] = set()
        dependency_files = {
            "requirements.txt",
            "pyproject.toml",
            "package.json",
            "package-lock.json",
            "pnpm-lock.yaml",
            "yarn.lock",
            ".env",
            ".env.example",
            "docker-compose.yml",
            "docker-compose.yaml",
        }

        for file_path in all_files:
            language = SOURCE_EXTENSIONS.get(file_path.suffix.lower())
            if language:
                language_counts[language] = language_counts.get(language, 0) + 1

            if file_path.name in dependency_files and file_path.stat().st_size < 2_000_000:
                text = file_path.read_text(encoding="utf-8", errors="ignore").lower()
                for db_name, patterns in DB_PATTERNS.items():
                    if any(pattern in text for pattern in patterns):
                        db_hits.add(db_name)

        primary_language = max(language_counts, key=language_counts.get) if language_counts else "unknown"
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_path": task.source_path,
            "workspace_path": task.workspace_path,
            "prompt": task.prompt,
            "total_files": len(all_files),
            "primary_language": primary_language,
            "language_breakdown": language_counts,
            "databases": sorted(db_hits),
            "security_findings": [],
        }

        profile_path = output_dir / "project-profile.json"
        findings_path = output_dir / "security-findings.json"
        report_path = output_dir / "intake-report.md"
        profile_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        findings_path.write_text("[]", encoding="utf-8")

        markdown = [
            "# Project Intake Report",
            "",
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}",
            f"Project Root: {task.workspace_path}",
            "",
            "## Summary",
            f"- Total files scanned: {len(all_files)}",
            f"- Primary language: {primary_language}",
            f"- Databases detected: {', '.join(sorted(db_hits)) if db_hits else 'none'}",
            "- Security findings: 0",
            "  - High: 0",
            "  - Medium: 0",
            "  - Low: 0",
            "",
            "## Language Breakdown",
        ]
        if language_counts:
            markdown.extend(f"- {name}: {count} file(s)" for name, count in sorted(language_counts.items()))
        else:
            markdown.append("- No recognized source files found")
        database_lines = [f"- {item}" for item in sorted(db_hits)] if db_hits else ["- none"]
        markdown.extend(
            [
                "",
                "## Database Signals",
                *database_lines,
                "",
                "## Requested Rebuild Prompt",
                task.prompt or "- none provided",
                "",
                "## Output Files",
                "- project-profile.json",
                "- security-findings.json",
                "- intake-report.md",
                "",
            ]
        )
        report_path.write_text("\n".join(markdown), encoding="utf-8")
        return report_path

    def _load_tasks(self) -> list[WorkspaceTask]:
        raw = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
        return [WorkspaceTask(**item) for item in raw]

    def _save_tasks(self, tasks: list[WorkspaceTask]) -> None:
        QUEUE_FILE.write_text(json.dumps([asdict(task) for task in tasks], indent=2), encoding="utf-8")

    def _has_internet(self) -> bool:
        try:
            urllib.request.urlopen("https://clients3.google.com/generate_204", timeout=3)
            return True
        except (urllib.error.URLError, TimeoutError, socket.timeout, OSError):
            return False


workspace_service = WorkspaceService()
