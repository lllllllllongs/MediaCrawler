from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PID_FILE = PROJECT_ROOT / "logs" / "webui.pid"


def windows_port_pids(port: int) -> set[int]:
    result = subprocess.run(
        ["netstat", "-ano"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    pids: set[int] = set()
    for line in result.stdout.splitlines():
        if f":{port}" not in line or "LISTENING" not in line:
            continue
        parts = line.split()
        if parts and parts[-1].isdigit():
            pids.add(int(parts[-1]))
    return pids


def stop_windows_pid(pid: int) -> int:
    result = subprocess.run(
        ["taskkill", "/PID", str(pid), "/T", "/F"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0 and "not found" not in result.stderr.lower():
        print(result.stdout.strip())
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


def main() -> int:
    pid = 0
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text(encoding="utf-8").strip())
        except ValueError:
            print("Invalid pid file will be removed.")

    try:
        if os.name == "nt":
            pids = set()
            if pid:
                pids.add(pid)
            pids.update(windows_port_pids(8080))
            if not pids:
                print("No WebUI process found on port 8080.")
            for target_pid in sorted(pids):
                stop_windows_pid(target_pid)
        else:
            if pid:
                os.kill(pid, signal.SIGTERM)
        time.sleep(1)
    except OSError as exc:
        print(f"Stop warning: {exc}", file=sys.stderr)
    finally:
        PID_FILE.unlink(missing_ok=True)

    print("Stopped WebUI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
