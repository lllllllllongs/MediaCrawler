from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "ai_manju_config.json"
RUN_LOG = PROJECT_ROOT / "logs" / "ai_manju_runs.jsonl"


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fp:
        config = json.load(fp)
    required = [
        "keywords",
        "platforms",
        "login_type",
        "save_data_option",
        "headless",
        "get_comments",
        "get_sub_comments",
        "max_notes_per_platform",
        "max_comments_per_item",
        "max_concurrency",
        "interval_seconds",
        "command_timeout_seconds",
        "creator_ids",
    ]
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"Missing required config keys: {', '.join(missing)}")
    return config


def bool_arg(value: bool) -> str:
    return "true" if value else "false"


def python_command() -> list[str]:
    venv_python = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return [str(venv_python)]
    return [sys.executable]


def append_run_log(record: dict[str, Any]) -> None:
    RUN_LOG.parent.mkdir(parents=True, exist_ok=True)
    with RUN_LOG.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(record, ensure_ascii=False) + "\n")


def run_command(command: list[str], label: str, dry_run: bool, timeout_seconds: int | None = None) -> int:
    started_at = now_iso()
    safe_label = label.replace(":", "_").replace("/", "_")
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    detail_log = log_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_label}.log"

    record: dict[str, Any] = {
        "label": label,
        "started_at": started_at,
        "command": command,
        "cwd": str(PROJECT_ROOT),
        "detail_log": str(detail_log),
        "dry_run": dry_run,
    }

    if dry_run:
        record["ended_at"] = now_iso()
        record["exit_code"] = 0
        append_run_log(record)
        print("[dry-run]", " ".join(command))
        return 0

    print(f"[{now_iso()}] start {label}")
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        completed = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env=env,
            timeout=timeout_seconds,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        exit_code = completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + f"\nCOMMAND TIMED OUT AFTER {timeout_seconds} SECONDS\n"
        exit_code = 124

    detail_log.write_text(
        "COMMAND: " + " ".join(command) + "\n\n"
        + "STDOUT:\n" + stdout + "\n\n"
        + "STDERR:\n" + stderr,
        encoding="utf-8",
    )

    record["ended_at"] = now_iso()
    record["exit_code"] = exit_code
    append_run_log(record)
    print(f"[{record['ended_at']}] end {label}, exit={exit_code}, log={detail_log}")
    return exit_code


def init_db(dry_run: bool) -> int:
    return run_command([*python_command(), "main.py", "--init_db", "sqlite"], "init_db:sqlite", dry_run, 300)


def search_command(platform: str, config: dict[str, Any]) -> list[str]:
    return [
        *python_command(),
        "main.py",
        "--platform",
        platform,
        "--lt",
        config["login_type"],
        "--type",
        "search",
        "--keywords",
        ",".join(config["keywords"]),
        "--get_comment",
        bool_arg(config["get_comments"]),
        "--get_sub_comment",
        bool_arg(config["get_sub_comments"]),
        "--headless",
        bool_arg(config["headless"]),
        "--save_data_option",
        config["save_data_option"],
        "--crawler_max_notes_count",
        str(config["max_notes_per_platform"]),
        "--max_comments_count_singlenotes",
        str(config["max_comments_per_item"]),
        "--max_concurrency_num",
        str(config["max_concurrency"]),
        "--enable_ip_proxy",
        "false",
    ]


def creator_command(platform: str, creator_ids: list[str], config: dict[str, Any]) -> list[str]:
    command = search_command(platform, config)
    type_index = command.index("--type") + 1
    command[type_index] = "creator"
    command.extend(["--creator_id", ",".join(creator_ids)])
    return command


def run_cycle(config: dict[str, Any], dry_run: bool) -> int:
    exit_code = 0
    timeout_seconds = int(config["command_timeout_seconds"])
    for platform in config["platforms"]:
        exit_code = max(
            exit_code,
            run_command(search_command(platform, config), f"{platform}:search", dry_run, timeout_seconds),
        )
        creator_ids = config["creator_ids"].get(platform, [])
        if creator_ids:
            exit_code = max(
                exit_code,
                run_command(creator_command(platform, creator_ids, config), f"{platform}:creator", dry_run, timeout_seconds),
            )
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AI manju MediaCrawler jobs.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--init-db", action="store_true", help="Initialize SQLite tables before crawling.")
    parser.add_argument("--once", action="store_true", help="Run one crawl cycle and exit.")
    parser.add_argument("--loop", action="store_true", help="Run forever with interval_seconds between cycles.")
    parser.add_argument("--dry-run", action="store_true", help="Print and log commands without executing them.")
    args = parser.parse_args()

    if not args.once and not args.loop and not args.init_db:
        parser.error("Choose at least one of --init-db, --once, or --loop.")

    config = load_config(args.config)
    exit_code = 0

    if args.init_db:
        exit_code = max(exit_code, init_db(args.dry_run))

    if args.once:
        exit_code = max(exit_code, run_cycle(config, args.dry_run))

    if args.loop:
        while True:
            exit_code = max(exit_code, run_cycle(config, args.dry_run))
            sleep_seconds = int(config["interval_seconds"])
            print(f"[{now_iso()}] sleep {sleep_seconds} seconds")
            time.sleep(sleep_seconds)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
