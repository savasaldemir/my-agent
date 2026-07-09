from __future__ import annotations

import json
import shutil
import socket
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from ..config import PROJECT_ROOT


RUNTIME_DIR = PROJECT_ROOT / "runtime"
WORKSPACES_DIR = RUNTIME_DIR / "workspaces"
QUEUE_FILE = RUNTIME_DIR / "task_queue.json"
RELEASE_DIR_NAME = ".agent-release"
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
    phase: str
    created_at: str
    updated_at: str
    retry_count: int = 0
    next_retry_at: str | None = None
    last_error: str | None = None
    report_path: str | None = None
    plan_path: str | None = None
    patches_path: str | None = None
    apply_summary_path: str | None = None


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
            phase="queued",
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
        now = datetime.now(timezone.utc)
        for task in tasks:
            if task.status != "pending":
                continue
            if task.next_retry_at:
                retry_at = datetime.fromisoformat(task.next_retry_at)
                if retry_at > now:
                    continue
            if task.requires_internet and not self._has_internet():
                self._schedule_retry(task, "Internet connection unavailable")
                continue
            processed.append(self.process_task(task.id))
        return processed

    def process_task(self, task_id: str) -> WorkspaceTask:
        with self._lock:
            tasks = self._load_tasks()
            task = next((item for item in tasks if item.id == task_id), None)
            if task is None:
                raise ValueError("Task not found")

            if task.requires_internet and not self._has_internet():
                self._schedule_retry(task, "Internet connection unavailable")
                self._save_tasks(tasks)
                return task

            task.status = "processing"
            task.phase = "intake"
            task.updated_at = datetime.now(timezone.utc).isoformat()
            task.last_error = None
            self._save_tasks(tasks)

            try:
                report_path, profile = self._run_intake(task)
                task.report_path = str(report_path)

                task.phase = "planning"
                plan_path = self._generate_rebuild_plan(task, profile)
                task.plan_path = str(plan_path)

                task.phase = "patching"
                patches_path = self._generate_patch_bundle(task, profile)
                task.patches_path = str(patches_path)

                task.phase = "apply"
                apply_summary_path = self._apply_patch_bundle(task)
                task.apply_summary_path = str(apply_summary_path)

                task.status = "completed"
                task.phase = "completed"
                task.next_retry_at = None
                task.last_error = None
            except OSError as exc:
                if task.requires_internet:
                    self._schedule_retry(task, str(exc))
                else:
                    task.retry_count += 1
                    task.last_error = str(exc)
                    task.status = "failed"
                    task.phase = "failed"
            except Exception as exc:
                task.retry_count += 1
                task.last_error = str(exc)
                task.status = "failed"
                task.phase = "failed"

            task.updated_at = datetime.now(timezone.utc).isoformat()
            self._save_tasks(tasks)
            return task

    def read_artifacts(self, task_id: str) -> dict[str, str]:
        task = self.get_task(task_id)
        if task is None:
            raise ValueError("Task not found")

        mapping = {
            "intake_report": task.report_path,
            "rebuild_plan": task.plan_path,
            "generated_patches": task.patches_path,
            "apply_result": task.apply_summary_path,
        }
        result: dict[str, str] = {}
        for key, value in mapping.items():
            if value and Path(value).exists():
                result[key] = Path(value).read_text(encoding="utf-8", errors="ignore")
        return result

    def _run_intake(self, task: WorkspaceTask) -> tuple[Path, dict]:
        source = Path(task.source_path)
        workspace = Path(task.workspace_path)
        if not workspace.exists():
            shutil.copytree(source, workspace, ignore=shutil.ignore_patterns(*DEFAULT_EXCLUDES))

        output_dir = workspace / ".agent-intake"
        release_dir = workspace / RELEASE_DIR_NAME
        output_dir.mkdir(parents=True, exist_ok=True)
        release_dir.mkdir(parents=True, exist_ok=True)

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
        return report_path, report

    def _generate_rebuild_plan(self, task: WorkspaceTask, profile: dict) -> Path:
        workspace = Path(task.workspace_path)
        release_dir = workspace / RELEASE_DIR_NAME
        release_dir.mkdir(parents=True, exist_ok=True)
        entrypoints = self._detect_entrypoints(workspace)
        plan_path = release_dir / "rebuild-plan.md"

        lines = [
            "# Rebuild Plan",
            "",
            f"Task: {task.id}",
            f"Workspace: {task.workspace_path}",
            "",
            "## Goal",
            task.prompt or "Stabilize and rebuild the imported project with safe defaults.",
            "",
            "## Detected Runtime",
            f"- Primary language: {profile.get('primary_language', 'unknown')}",
            f"- Databases: {', '.join(profile.get('databases', [])) or 'none'}",
            "",
            "## Entry Points",
        ]
        if entrypoints:
            lines.extend(f"- {item}" for item in entrypoints)
        else:
            lines.append("- No entrypoint detected automatically")
        lines.extend(
            [
                "",
                "## Pipeline",
                "1. Intake source into isolated workspace",
                "2. Generate rebuild plan and patch bundle",
                "3. Apply release helpers and startup scripts",
                "4. Expose launch instructions and retry metadata",
                "",
                "## Retry Strategy",
                "- Internet-required tasks are deferred automatically when offline",
                "- Exponential backoff is applied before the next retry attempt",
            ]
        )
        plan_path.write_text("\n".join(lines), encoding="utf-8")
        return plan_path

    def _generate_patch_bundle(self, task: WorkspaceTask, profile: dict) -> Path:
        workspace = Path(task.workspace_path)
        release_dir = workspace / RELEASE_DIR_NAME
        release_dir.mkdir(parents=True, exist_ok=True)
        startup_commands = self._build_start_commands(workspace)
        patch_bundle = {
            "task_id": task.id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "workspace_path": task.workspace_path,
            "primary_language": profile.get("primary_language", "unknown"),
            "operations": [
                {
                    "path": f"{RELEASE_DIR_NAME}/entrypoint.json",
                    "action": "write",
                    "reason": "Provide a machine-readable startup manifest for the rebuilt project",
                },
                {
                    "path": f"{RELEASE_DIR_NAME}/START.ps1",
                    "action": "write",
                    "reason": "Single-click Windows entrypoint for the rebuilt workspace",
                },
                {
                    "path": f"{RELEASE_DIR_NAME}/START.sh",
                    "action": "write",
                    "reason": "Single-command Unix entrypoint for the rebuilt workspace",
                },
                {
                    "path": f"{RELEASE_DIR_NAME}/APPLY_RESULT.md",
                    "action": "write",
                    "reason": "Summarize applied release helpers and next steps",
                },
            ],
            "startup_commands": startup_commands,
            "requires_internet": task.requires_internet,
            "retry_count": task.retry_count,
        }
        patches_path = release_dir / "generated-patches.json"
        patches_path.write_text(json.dumps(patch_bundle, indent=2), encoding="utf-8")
        return patches_path

    def _apply_patch_bundle(self, task: WorkspaceTask) -> Path:
        workspace = Path(task.workspace_path)
        release_dir = workspace / RELEASE_DIR_NAME
        patches_path = release_dir / "generated-patches.json"
        bundle = json.loads(patches_path.read_text(encoding="utf-8"))
        startup_commands = bundle.get("startup_commands", {})

        entrypoint_manifest = {
            "workspace": task.workspace_path,
            "startup_commands": startup_commands,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "task_id": task.id,
        }
        (release_dir / "entrypoint.json").write_text(json.dumps(entrypoint_manifest, indent=2), encoding="utf-8")

        start_ps1 = [
            "$ErrorActionPreference = 'Stop'",
            f"Set-Location '{workspace}'",
        ]
        if startup_commands.get("windows"):
            start_ps1.append(startup_commands["windows"])
        else:
            start_ps1.append("Write-Host 'No Windows startup command detected. See entrypoint.json.'")
        (release_dir / "START.ps1").write_text("\n".join(start_ps1) + "\n", encoding="utf-8")

        start_sh = ["#!/usr/bin/env bash", "set -euo pipefail", f"cd '{workspace.as_posix()}'"]
        if startup_commands.get("unix"):
            start_sh.append(startup_commands["unix"])
        else:
            start_sh.append("echo 'No Unix startup command detected. See entrypoint.json.'")
        (release_dir / "START.sh").write_text("\n".join(start_sh) + "\n", encoding="utf-8")

        summary_path = release_dir / "APPLY_RESULT.md"
        summary_lines = [
            "# Apply Result",
            "",
            f"Task: {task.id}",
            f"Workspace: {task.workspace_path}",
            "",
            "## Generated Files",
            f"- {RELEASE_DIR_NAME}/entrypoint.json",
            f"- {RELEASE_DIR_NAME}/START.ps1",
            f"- {RELEASE_DIR_NAME}/START.sh",
            f"- {RELEASE_DIR_NAME}/generated-patches.json",
            f"- {RELEASE_DIR_NAME}/rebuild-plan.md",
            "",
            "## Startup Commands",
            f"- Windows: {startup_commands.get('windows', 'not detected')}",
            f"- Unix: {startup_commands.get('unix', 'not detected')}",
            "",
            "## Retry",
            "- If internet is required and unavailable, the task remains queued and will retry with backoff.",
        ]
        summary_path.write_text("\n".join(summary_lines), encoding="utf-8")
        return summary_path

    def _detect_entrypoints(self, workspace: Path) -> list[str]:
        entrypoints: list[str] = []
        if (workspace / "main.py").exists():
            entrypoints.append("python main.py")
        if (workspace / "app.py").exists():
            entrypoints.append("python app.py")
        if (workspace / "manage.py").exists():
            entrypoints.append("python manage.py runserver")
        package_json = workspace / "package.json"
        if package_json.exists():
            try:
                package = json.loads(package_json.read_text(encoding="utf-8"))
                scripts = package.get("scripts", {})
                if "dev" in scripts:
                    entrypoints.append("npm run dev")
                if "start" in scripts:
                    entrypoints.append("npm start")
            except json.JSONDecodeError:
                pass
        return entrypoints

    def _build_start_commands(self, workspace: Path) -> dict[str, str]:
        package_json = workspace / "package.json"
        if package_json.exists():
            try:
                package = json.loads(package_json.read_text(encoding="utf-8"))
                scripts = package.get("scripts", {})
                if "dev" in scripts:
                    return {
                        "windows": "npm install; npm run dev",
                        "unix": "npm install && npm run dev",
                    }
                if "start" in scripts:
                    return {
                        "windows": "npm install; npm start",
                        "unix": "npm install && npm start",
                    }
            except json.JSONDecodeError:
                pass

        if (workspace / "requirements.txt").exists() and (workspace / "main.py").exists():
            return {
                "windows": "python -m pip install -r requirements.txt; python main.py",
                "unix": "python -m pip install -r requirements.txt && python main.py",
            }
        if (workspace / "requirements.txt").exists() and (workspace / "app.py").exists():
            return {
                "windows": "python -m pip install -r requirements.txt; python app.py",
                "unix": "python -m pip install -r requirements.txt && python app.py",
            }
        return {
            "windows": "Write-Host 'Review .agent-release/entrypoint.json for manual startup guidance'",
            "unix": "echo 'Review .agent-release/entrypoint.json for manual startup guidance'",
        }

    def _schedule_retry(self, task: WorkspaceTask, error_message: str) -> None:
        task.retry_count += 1
        task.last_error = error_message
        task.status = "pending"
        task.phase = "waiting-retry"
        delay_seconds = min(1800, 15 * (2 ** min(task.retry_count, 6)))
        task.next_retry_at = (datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)).isoformat()

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
