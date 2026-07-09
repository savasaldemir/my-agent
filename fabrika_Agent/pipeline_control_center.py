from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent
AGENT_WEB_URL = "http://127.0.0.1:3000"
WORKSPACE_API_BASE = "http://127.0.0.1:8000/api/v1/workspaces"


class FabrikaPipelineControlCenter:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Fabrika Agent Pipeline Center")
        self.root.geometry("1220x780")
        self.root.configure(bg="#0f172a")
        self.agent_process: subprocess.Popen[str] | None = None
        self.tasks: list[dict[str, object]] = []
        self._configure_style()
        self._build_ui()
        self._set_status("Hazır")
        self.refresh_tasks()

    def _configure_style(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TFrame", background="#0f172a")
        style.configure("TLabel", background="#0f172a", foreground="#e5e7eb", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI Semibold", 16), foreground="#f8fafc")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)
        ttk.Label(container, text="Fabrika Agent Pipeline Center", style="Header.TLabel").pack(anchor=tk.W)
        ttk.Label(container, text="Legacy GUI + modern AGENT pipeline + retry/backoff aware rebuild flow").pack(anchor=tk.W, pady=(4, 12))

        actions = ttk.Frame(container)
        actions.pack(fill=tk.X, pady=(0, 12))
        ttk.Button(actions, text="AGENT Stack Başlat", command=self.start_agent_stack).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(actions, text="AGENT Web UI Aç", command=lambda: webbrowser.open(AGENT_WEB_URL)).pack(side=tk.LEFT, padx=8)
        ttk.Button(actions, text="Legacy Fabrika GUI Aç", command=self.open_legacy_gui).pack(side=tk.LEFT, padx=8)
        ttk.Button(actions, text="Görevleri Yenile", command=self.refresh_tasks).pack(side=tk.LEFT, padx=8)
        ttk.Button(actions, text="Bekleyenleri İşlet", command=self.process_queue).pack(side=tk.LEFT, padx=8)

        form = ttk.Frame(container)
        form.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(form, text="Kaynak Proje Klasörü").grid(row=0, column=0, sticky="w")
        self.source_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.source_var, width=90).grid(row=1, column=0, sticky="we", padx=(0, 8))
        ttk.Button(form, text="Klasör Seç", command=self.pick_source_folder).grid(row=1, column=1)

        ttk.Label(form, text="Rebuild Prompt").grid(row=2, column=0, sticky="w", pady=(12, 0))
        self.prompt_text = tk.Text(form, height=6, bg="#111827", fg="#e5e7eb", insertbackground="#e5e7eb")
        self.prompt_text.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.prompt_text.insert("1.0", "Projeyi güvenli, modern, çalıştırılabilir ve bakım yapılabilir hale getir.")

        self.requires_internet = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            form,
            text="İnternet gerekiyorsa otomatik retry/backoff ile beklesin",
            variable=self.requires_internet,
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(12, 0))

        submit_bar = ttk.Frame(container)
        submit_bar.pack(fill=tk.X, pady=(0, 12))
        ttk.Button(submit_bar, text="Intake + Pipeline Çalıştır", command=self.run_intake).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(submit_bar, text="Yalnız Kuyruğa Ekle", command=self.enqueue_task).pack(side=tk.LEFT, padx=8)

        panes = ttk.Panedwindow(container, orient=tk.HORIZONTAL)
        panes.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(panes, padding=8)
        right = ttk.Frame(panes, padding=8)
        panes.add(left, weight=1)
        panes.add(right, weight=1)

        self.task_tree = ttk.Treeview(left, columns=("source", "status", "phase", "retry"), show="headings")
        self.task_tree.heading("source", text="Source")
        self.task_tree.heading("status", text="Status")
        self.task_tree.heading("phase", text="Phase")
        self.task_tree.heading("retry", text="Retry")
        self.task_tree.column("source", width=320)
        self.task_tree.column("status", width=120)
        self.task_tree.column("phase", width=150)
        self.task_tree.column("retry", width=80, anchor=tk.CENTER)
        self.task_tree.pack(fill=tk.BOTH, expand=True)
        self.task_tree.bind("<<TreeviewSelect>>", self.on_task_selected)

        self.output_text = tk.Text(right, bg="#111827", fg="#e5e7eb", insertbackground="#e5e7eb")
        self.output_text.pack(fill=tk.BOTH, expand=True)

        footer = ttk.Frame(container)
        footer.pack(fill=tk.X, pady=(12, 0))
        self.status_label = ttk.Label(footer, text="")
        self.status_label.pack(side=tk.LEFT)

    def _set_status(self, message: str) -> None:
        self.status_label.config(text=message)

    def _append_output(self, text: str) -> None:
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)

    def _api_request(self, method: str, path: str, payload: dict | None = None, retries: int = 5) -> dict | list:
        delays = [0, 1, 2, 4, 8]
        last_error: Exception | None = None
        for attempt in range(min(retries, len(delays))):
            try:
                data = None
                headers = {}
                if payload is not None:
                    data = json.dumps(payload).encode("utf-8")
                    headers["Content-Type"] = "application/json"
                request = urllib.request.Request(f"{WORKSPACE_API_BASE}{path}", data=data, headers=headers, method=method)
                with urllib.request.urlopen(request, timeout=20) as response:
                    raw = response.read().decode("utf-8")
                    return json.loads(raw) if raw else {}
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = exc
                if attempt == min(retries, len(delays)) - 1:
                    break
                time.sleep(delays[attempt + 1])
        raise RuntimeError(f"API request failed: {last_error}")

    def start_agent_stack(self) -> None:
        if self.agent_process and self.agent_process.poll() is None:
            self._set_status("AGENT stack zaten çalışıyor")
            return
        launcher = REPO_ROOT / "launch_agent.py"
        self.agent_process = subprocess.Popen([sys.executable, str(launcher), "--skip-build"], cwd=str(REPO_ROOT))
        self._set_status("AGENT stack başlatılıyor")

    def open_legacy_gui(self) -> None:
        legacy = BASE_DIR / "yerel_fabrika_gui.py"
        subprocess.Popen([sys.executable, str(legacy)], cwd=str(BASE_DIR))
        self._set_status("Legacy Fabrika GUI açıldı")

    def pick_source_folder(self) -> None:
        selected = filedialog.askdirectory(title="Project folder")
        if selected:
            self.source_var.set(selected)

    def refresh_tasks(self) -> None:
        def work() -> None:
            try:
                tasks = self._api_request("GET", "/tasks")
                self.tasks = tasks if isinstance(tasks, list) else []
                self.task_tree.delete(*self.task_tree.get_children())
                for task in self.tasks:
                    self.task_tree.insert(
                        "",
                        tk.END,
                        iid=task["id"],
                        values=(task["source_path"], task["status"], task.get("phase", "-"), task.get("retry_count", 0)),
                    )
                self._set_status("Görev listesi güncellendi")
            except Exception as exc:
                self._set_status(f"Görevler alınamadı: {exc}")

        threading.Thread(target=work, daemon=True).start()

    def _submit_intake(self, requires_internet: bool) -> None:
        source_path = self.source_var.get().strip()
        if not source_path:
            messagebox.showwarning("Eksik", "Önce bir kaynak proje klasörü seçin.", parent=self.root)
            return
        payload = {
            "source_path": source_path,
            "prompt": self.prompt_text.get("1.0", tk.END).strip(),
            "requires_internet": requires_internet,
        }

        def work() -> None:
            self.output_text.delete("1.0", tk.END)
            try:
                task = self._api_request("POST", "/intake", payload)
                self._append_output(json.dumps(task, indent=2, ensure_ascii=False))
                self.refresh_tasks()
                self.load_task_artifacts(task["id"])
                self._set_status("Intake görevi oluşturuldu")
            except Exception as exc:
                self._append_output(f"Intake failed: {exc}")
                self._set_status("Intake başarısız")

        threading.Thread(target=work, daemon=True).start()

    def run_intake(self) -> None:
        self._submit_intake(self.requires_internet.get())

    def enqueue_task(self) -> None:
        self._submit_intake(True)

    def process_queue(self) -> None:
        def work() -> None:
            try:
                result = self._api_request("POST", "/tasks/process")
                self._append_output(json.dumps(result, indent=2, ensure_ascii=False))
                self.refresh_tasks()
                self._set_status("Bekleyen görevler işlendi")
            except Exception as exc:
                self._append_output(f"Queue processing failed: {exc}")
                self._set_status("Kuyruk işleme başarısız")

        threading.Thread(target=work, daemon=True).start()

    def on_task_selected(self, _event: object) -> None:
        selection = self.task_tree.selection()
        if not selection:
            return
        self.load_task_artifacts(selection[0])

    def load_task_artifacts(self, task_id: str) -> None:
        def work() -> None:
            try:
                task = self._api_request("GET", f"/tasks/{urllib.parse.quote(task_id)}")
                artifacts = self._api_request("GET", f"/tasks/{urllib.parse.quote(task_id)}/artifacts")
                self.output_text.delete("1.0", tk.END)
                self._append_output("# Task\n")
                self._append_output(json.dumps(task, indent=2, ensure_ascii=False))
                for title, content in artifacts.items():
                    self._append_output(f"\n# {title}\n")
                    self._append_output(str(content))
                self._set_status("Task detayları yüklendi")
            except Exception as exc:
                self._append_output(f"Artifact load failed: {exc}")
                self._set_status("Task detayları alınamadı")

        threading.Thread(target=work, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    FabrikaPipelineControlCenter(root)
    root.mainloop()
