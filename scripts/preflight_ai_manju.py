from __future__ import annotations

import json
import shutil
import socket
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "ai_manju_config.json"
DB_PATH = PROJECT_ROOT / "database" / "sqlite_tables.db"


def check_port(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        return sock.connect_ex((host, port)) == 0


def main() -> int:
    ok = True

    uv_path = shutil.which("uv")
    print(f"uv: {uv_path or 'missing'}")
    ok = ok and bool(uv_path)

    if CONFIG_PATH.exists():
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        print(f"config: {CONFIG_PATH}")
        print(f"platforms: {', '.join(config['platforms'])}")
        print(f"keywords: {', '.join(config['keywords'])}")
        print(f"interval_seconds: {config['interval_seconds']}")
        print(f"command_timeout_seconds: {config['command_timeout_seconds']}")
    else:
        print(f"config: missing ({CONFIG_PATH})")
        ok = False

    print(f"sqlite: {DB_PATH if DB_PATH.exists() else 'missing; run --init-db first'}")
    ok = ok and DB_PATH.exists()

    cdp_ready = check_port("127.0.0.1", 9222)
    print(f"chrome_cdp_9222: {'ready' if cdp_ready else 'not reachable'}")
    if not cdp_ready:
        print("hint: open Chrome/Edge remote debugging before live crawling, or allow MediaCrawler to wait for it.")

    try:
        result = subprocess.run(
            [sys.executable, "-c", "import playwright, sqlalchemy, aiosqlite; print('python_deps: ready')"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        print(result.stdout.strip() or result.stderr.strip())
        ok = ok and result.returncode == 0
    except Exception as exc:
        print(f"python_deps: failed ({exc})")
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
