from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "logs"
PID_FILE = LOG_DIR / "webui.pid"
OUT_LOG = LOG_DIR / "webui-background.out.log"
ERR_LOG = LOG_DIR / "webui-background.err.log"


def is_pid_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def main() -> int:
    LOG_DIR.mkdir(exist_ok=True)

    if PID_FILE.exists():
        try:
            old_pid = int(PID_FILE.read_text(encoding="utf-8").strip())
        except ValueError:
            old_pid = 0
        if old_pid and is_pid_running(old_pid):
            print(f"WebUI already appears to be running, pid={old_pid}")
            return 0
        PID_FILE.unlink(missing_ok=True)

    python = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    if not python.exists():
        print(f"Virtualenv Python not found: {python}", file=sys.stderr)
        return 1

    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    with OUT_LOG.open("ab") as stdout, ERR_LOG.open("ab") as stderr:
        process = subprocess.Popen(
            [
                str(python),
                "-m",
                "uvicorn",
                "api.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8080",
            ],
            cwd=PROJECT_ROOT,
            stdout=stdout,
            stderr=stderr,
            stdin=subprocess.DEVNULL,
            creationflags=creationflags,
            close_fds=False,
        )

    PID_FILE.write_text(str(process.pid), encoding="utf-8")
    time.sleep(1)
    if process.poll() is not None:
        print(f"WebUI exited immediately with code {process.returncode}. See {ERR_LOG}", file=sys.stderr)
        return process.returncode or 1

    print(f"Started WebUI pid={process.pid}")
    print("URL: http://127.0.0.1:8080")
    print(f"stdout: {OUT_LOG}")
    print(f"stderr: {ERR_LOG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
