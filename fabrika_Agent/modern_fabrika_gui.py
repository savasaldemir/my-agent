from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from dataclasses import dataclass, asdict
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent
QUEUE_PATH = BASE_DIR / "task_queue.json"
WORKSPACES_DIR = BASE_DIR / "workspaces"
AGENT_URL = "http://127.0.0.1:3000"
POWERSHELL = Path("C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe")


@dataclass
class QueueTask:
    source_path: str
    workspace_path: str
    prompt: str
    requires_internet: bool
    created_at: float
    status: str = "pending"


class FabrikaControlCenter:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Fabrika Agent Control Center")
        self.root.geometry("1180x760")
        self.root.configure(bg="#111827")
        self.agent_process: subprocess.Popen[str] | None = None
        self.queue: list[QueueTask] = self._load_queue()
        WORKSPACES_DIR.mkdir(exist_ok=True)
        self._configure_style()
        self._build_ui()
        self._refresh_queue_view()
        self._set_status("Hazır")

    def _configure_style(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TFrame", background="#111827")
        style.configure("TLabel", background="#111827", foreground="#E5E7EB", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI Semibold", 16), foreground="#F9FAFB")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="Fabrika Agent Control Center", style="Header.TLabel").pack(anchor=tk.W)
        ttk.Label(
            container,
            text="Legacy factory UI + modern AGENT altyapisi + kuyruklu proje intake akisi",
        ).pack(anchor=tk.W, pady=(4, 12))

        notebook = ttk.Notebook(container)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.stack_tab = ttk.Frame(notebook, padding=12)
        self.intake_tab = ttk.Frame(notebook, padding=12)
        self.queue_tab = ttk.Frame(notebook, padding=12)
        notebook.add(self.stack_tab, text="AGENT Stack")
        notebook.add(self.intake_tab, text="Project Intake")
        notebook.add(self.queue_tab, text="Queued Tasks")

        self._build_stack_tab()
        self._build_intake_tab()
        self._build_queue_tab()

        status_frame = ttk.Frame(container)
        status_frame.pack(fill=tk.X, pady=(12, 0))
        self.status_label = ttk.Label(status_frame, text="")
        self.status_label.pack(side=tk.LEFT)

    def _build_stack_tab(self) -> None:
        ttk.Label(self.stack_tab, text="AGENT uygulamasini tek yerden baslatin ve yonetin.").pack(anchor=tk.W, pady=(0, 12))
        buttons = ttk.Frame(self.stack_tab)
        buttons.pack(fill=tk.X, pady=(0, 12))

        ttk.Button(buttons, text="AGENT Stack Baslat", command=self.start_agent_stack).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(buttons, text="AGENT Web UI Ac", command=lambda: webbrowser.open(AGENT_URL)).pack(side=tk.LEFT, padx=8)
        ttk.Button(buttons, text="Legacy Fabrika GUI Ac", command=self.open_legacy_gui).pack(side=tk.LEFT, padx=8)
        ttk.Button(buttons, text="Saglik Kontrolu", command=self.check_agent_health).pack(side=tk.LEFT, padx=8)

        self.health_text = tk.Text(self.stack_tab, height=28, bg="#0F172A", fg="#E5E7EB", insertbackground="#E5E7EB")
        self.health_text.pack(fill=tk.BOTH, expand=True)

    def _build_intake_tab(self) -> None:
        form = ttk.Frame(self.intake_tab)
        form.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(form, text="Kaynak Proje Klasoru").grid(row=0, column=0, sticky="w")
        self.source_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.source_var, width=90).grid(row=1, column=0, padx=(0, 8), sticky="we")
        ttk.Button(form, text="Klasor Sec", command=self.pick_source_folder).grid(row=1, column=1)

        ttk.Label(form, text="Yeniden Uretim Notu / Prompt").grid(row=2, column=0, sticky="w", pady=(12, 0))
        self.prompt_text = tk.Text(form, height=6, bg="#0F172A", fg="#E5E7EB", insertbackground="#E5E7EB")
        self.prompt_text.grid(row=3, column=0, columnspan=2, sticky="nsew")

        self.internet_required = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            form,
            text="Bu islem internet gerektiriyorsa kuyrukta beklesin, internet geldiginde devam etsin",
            variable=self.internet_required,
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(12, 0))

        actions = ttk.Frame(self.intake_tab)
        actions.pack(fill=tk.X, pady=(12, 12))
        ttk.Button(actions, text="Workspace'e Al ve Intake Calistir", command=self.import_and_intake).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(actions, text="Task Olarak Kuyruga Ekle", command=self.enqueue_current_task).pack(side=tk.LEFT, padx=8)

        self.intake_output = tk.Text(self.intake_tab, bg="#0F172A", fg="#E5E7EB", insertbackground="#E5E7EB")
        self.intake_output.pack(fill=tk.BOTH, expand=True)

    def _build_queue_tab(self) -> None:
        actions = ttk.Frame(self.queue_tab)
        actions.pack(fill=tk.X, pady=(0, 12))
        ttk.Button(actions, text="Bekleyen Gorevleri Islet", command=self.process_queue).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(actions, text="Kuyrugu Yenile", command=self._refresh_queue_view).pack(side=tk.LEFT)

        self.queue_tree = ttk.Treeview(self.queue_tab, columns=("source", "workspace", "internet", "status"), show="headings")
        self.queue_tree.heading("source", text="Source")
        self.queue_tree.heading("workspace", text="Workspace")
        self.queue_tree.heading("internet", text="Internet")
        self.queue_tree.heading("status", text="Status")
        self.queue_tree.column("source", width=280)
        self.queue_tree.column("workspace", width=280)
        self.queue_tree.column("internet", width=120, anchor=tk.CENTER)
        self.queue_tree.column("status", width=120, anchor=tk.CENTER)
        self.queue_tree.pack(fill=tk.BOTH, expand=True)

    def _set_status(self, message: str) -> None:
        self.status_label.config(text=message)

    def _append_output(self, widget: tk.Text, text: str) -> None:
        widget.insert(tk.END, text + "\n")
        widget.see(tk.END)

    def _load_queue(self) -> list[QueueTask]:
        if not QUEUE_PATH.exists():
            return []
        try:
            data = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
            return [QueueTask(**item) for item in data]
        except Exception:
            return []

    def _save_queue(self) -> None:
        QUEUE_PATH.write_text(json.dumps([asdict(task) for task in self.queue], indent=2), encoding="utf-8")

    def _refresh_queue_view(self) -> None:
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)
        for task in self.queue:
            self.queue_tree.insert(
                "",
                tk.END,
                values=(task.source_path, task.workspace_path, "yes" if task.requires_internet else "no", task.status),
            )

    def pick_source_folder(self) -> None:
        selected = filedialog.askdirectory(title="Project folder")
        if selected:
            self.source_var.set(selected)

    def open_legacy_gui(self) -> None:
        legacy = BASE_DIR / "yerel_fabrika_gui.py"
        subprocess.Popen([sys.executable, str(legacy)], cwd=str(BASE_DIR))
        self._set_status("Legacy Fabrika GUI baslatildi")

    def start_agent_stack(self) -> None:
        if self.agent_process and self.agent_process.poll() is None:
            self._set_status("AGENT stack zaten calisiyor")
            return

        launcher = REPO_ROOT / "launch_agent.py"
        self.agent_process = subprocess.Popen([sys.executable, str(launcher), "--skip-build"], cwd=str(REPO_ROOT))
        self._append_output(self.health_text, "AGENT stack baslatiliyor...")
        self._set_status("AGENT stack baslatiliyor")

    def check_agent_health(self) -> None:
        def work() -> None:
            self.health_text.delete("1.0", tk.END)
            try:
                with urllib.request.urlopen(f"{AGENT_URL}/health", timeout=3) as response:
                    self._append_output(self.health_text, response.read().decode("utf-8"))
                    self._set_status("AGENT stack saglikli")
            except Exception as exc:
                self._append_output(self.health_text, f"Health check failed: {exc}")
                self._set_status("AGENT stack erisilemedi")

        threading.Thread(target=work, daemon=True).start()

    def _has_internet(self) -> bool:
        try:
            with urllib.request.urlopen("https://clients3.google.com/generate_204", timeout=3):
                return True
        except Exception:
            return False

    def _ensure_workspace_copy(self, source: Path) -> Path:
        workspace = WORKSPACES_DIR / f"{source.name}-{int(time.time())}"
        shutil.copytree(source, workspace, dirs_exist_ok=True)
        return workspace

    def _run_intake_for_workspace(self, workspace: Path) -> str:
        command = [
            str(POWERSHELL),
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(REPO_ROOT / "scripts" / "project-intake.ps1"),
            "-ProjectPath",
            str(workspace),
        ]
        completed = subprocess.run(command, cwd=str(REPO_ROOT), capture_output=True, text=True)
        report = workspace / ".agent-intake" / "intake-report.md"
        details = completed.stdout + "\n" + completed.stderr
        if report.exists():
            details += "\n\n" + report.read_text(encoding="utf-8")
        return details.strip()

    def import_and_intake(self) -> None:
        source_text = self.source_var.get().strip()
        if not source_text:
            messagebox.showwarning("Eksik", "Once bir kaynak proje klasoru secin.", parent=self.root)
            return

        source = Path(source_text)
        if not source.exists():
            messagebox.showerror("Hata", "Secilen klasor bulunamadi.", parent=self.root)
            return

        def work() -> None:
            self.intake_output.delete("1.0", tk.END)
            try:
                workspace = self._ensure_workspace_copy(source)
                self._append_output(self.intake_output, f"Workspace hazirlandi: {workspace}")
                report_text = self._run_intake_for_workspace(workspace)
                self._append_output(self.intake_output, report_text)
                self._set_status("Workspace intake tamamlandi")
            except Exception as exc:
                self._append_output(self.intake_output, f"Intake failed: {exc}")
                self._set_status("Intake basarisiz")

        threading.Thread(target=work, daemon=True).start()

    def enqueue_current_task(self) -> None:
        source_text = self.source_var.get().strip()
        if not source_text:
            messagebox.showwarning("Eksik", "Once bir kaynak proje klasoru secin.", parent=self.root)
            return

        source = Path(source_text)
        if not source.exists():
            messagebox.showerror("Hata", "Secilen klasor bulunamadi.", parent=self.root)
            return

        workspace = WORKSPACES_DIR / f"{source.name}-queued-{int(time.time())}"
        task = QueueTask(
            source_path=str(source),
            workspace_path=str(workspace),
            prompt=self.prompt_text.get("1.0", tk.END).strip(),
            requires_internet=self.internet_required.get(),
            created_at=time.time(),
        )
        self.queue.append(task)
        self._save_queue()
        self._refresh_queue_view()
        self._set_status("Task kuyruga eklendi")

    def process_queue(self) -> None:
        def work() -> None:
            internet_available = self._has_internet()
            changed = False
            for task in self.queue:
                if task.status != "pending":
                    continue
                if task.requires_internet and not internet_available:
                    continue
                try:
                    source = Path(task.source_path)
                    workspace = Path(task.workspace_path)
                    if not workspace.exists():
                        shutil.copytree(source, workspace, dirs_exist_ok=True)
                    report_text = self._run_intake_for_workspace(workspace)
                    self._append_output(self.intake_output, f"[Task] {source.name}\n{report_text}\n")
                    task.status = "done"
                    changed = True
                except Exception as exc:
                    task.status = f"failed: {exc}"
                    changed = True
            if changed:
                self._save_queue()
                self._refresh_queue_view()
            self._set_status("Kuyruk isleme tamamlandi")

        threading.Thread(target=work, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = FabrikaControlCenter(root)
    root.mainloop()
