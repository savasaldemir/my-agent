from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
BACKEND_VENV_PYTHON = REPO_ROOT / "backend" / "venv" / "Scripts" / "python.exe"
GATEWAY_DIR = REPO_ROOT / "backend" / "api-gateway"
WEB_DIR = REPO_ROOT / "frontend" / "web"
GATEWAY_DIST = GATEWAY_DIR / "dist" / "index.js"
NODE_PATHS = [
    Path("C:/Program Files/nodejs/node.exe"),
    Path("C:/Program Files/nodejs/node.cmd"),
]
NPM_PATHS = [
    Path("C:/Program Files/nodejs/npm.cmd"),
]


def find_first_existing(paths: list[Path]) -> Path | None:
    for candidate in paths:
        if candidate.exists():
            return candidate
    return None


def http_ready(url: str, timeout_seconds: float = 1.5) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
            return 200 <= response.status < 500
    except Exception:
        return False


def wait_for_http(url: str, label: str, max_seconds: int = 60) -> None:
    started = time.time()
    while time.time() - started < max_seconds:
        if http_ready(url):
            print(f"[ok] {label} is ready: {url}")
            return
        time.sleep(1)
    raise RuntimeError(f"Timed out waiting for {label}: {url}")


def run_checked(command: list[str], cwd: Path) -> None:
    print("[run]", " ".join(command))
    subprocess.run(command, cwd=str(cwd), check=True)


def ensure_build(node: Path, npm: Path, skip_build: bool) -> None:
    if skip_build:
        return

    env = os.environ.copy()
    env["Path"] = str(node.parent) + os.pathsep + env.get("Path", "")

    print("[build] Building frontend/web...")
    subprocess.run([str(npm), "install"], cwd=str(WEB_DIR), check=True, env=env)
    subprocess.run([str(npm), "run", "build"], cwd=str(WEB_DIR), check=True, env=env)

    print("[build] Building backend/api-gateway...")
    subprocess.run([str(npm), "install"], cwd=str(GATEWAY_DIR), check=True, env=env)
    subprocess.run([str(npm), "run", "build"], cwd=str(GATEWAY_DIR), check=True, env=env)


def start_processes(node: Path) -> tuple[subprocess.Popen[str], subprocess.Popen[str]]:
    if not BACKEND_VENV_PYTHON.exists():
        raise FileNotFoundError(
            f"Backend venv python not found: {BACKEND_VENV_PYTHON}. Run scripts/bootstrap-local.ps1 first."
        )
    if not GATEWAY_DIST.exists():
        raise FileNotFoundError(
            f"Gateway dist not found: {GATEWAY_DIST}. Build the project first or rerun without --skip-build."
        )

    env = os.environ.copy()
    env["Path"] = str(node.parent) + os.pathsep + env.get("Path", "")

    backend = subprocess.Popen(
        [
            str(BACKEND_VENV_PYTHON),
            "-m",
            "uvicorn",
            "backend.core.app:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=str(REPO_ROOT),
        env=env,
    )

    gateway = subprocess.Popen(
        [str(node), str(GATEWAY_DIST)],
        cwd=str(GATEWAY_DIR),
        env=env,
    )

    return backend, gateway


def stop_process(process: subprocess.Popen[str] | None) -> None:
    if not process or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch the AGENT web application stack")
    parser.add_argument("--skip-build", action="store_true", help="Skip frontend/gateway build steps")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser automatically")
    args = parser.parse_args()

    node = find_first_existing(NODE_PATHS)
    npm = find_first_existing(NPM_PATHS)
    if not node or not npm:
        raise FileNotFoundError("Node.js/npm not found. Install Node.js LTS first.")

    ensure_build(node, npm, args.skip_build)
    backend = None
    gateway = None
    try:
        backend, gateway = start_processes(node)
        wait_for_http("http://127.0.0.1:8000/health", "Core API")
        wait_for_http("http://127.0.0.1:3000/health", "Gateway/UI")

        app_url = "http://127.0.0.1:3000"
        print(f"[ready] AGENT is running at {app_url}")
        if not args.no_browser:
            webbrowser.open(app_url)

        def handle_signal(_signum: int, _frame: object) -> None:
            stop_process(gateway)
            stop_process(backend)
            raise SystemExit(0)

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

        while True:
            if backend.poll() is not None:
                raise RuntimeError("Backend process exited unexpectedly")
            if gateway.poll() is not None:
                raise RuntimeError("Gateway process exited unexpectedly")
            time.sleep(1)
    finally:
        stop_process(gateway)
        stop_process(backend)


if __name__ == "__main__":
    raise SystemExit(main())
