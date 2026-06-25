# AI Manju Crawl Runbook

This folder is configured to crawl AI manju related public data from Xiaohongshu, Douyin, and Kuaishou through MediaCrawler.

## Configure

Edit `ai_manju_config.json`:

- `keywords`: comma-free keyword list used by search mode.
- `creator_ids`: optional creator homepage URLs or IDs per platform.
- `max_notes_per_platform`: default `100`.
- `max_comments_per_item`: default `50`.
- `interval_seconds`: default `21600` (6 hours).

## Run

Initialize SQLite and run one cycle:

```powershell
.\start-ai-manju-once.ps1
```

Run continuously every 6 hours:

```powershell
.\start-ai-manju-loop.ps1
```

Preview commands without crawling:

```powershell
.\.venv\Scripts\python.exe scripts\ai_manju_runner.py --init-db --once --dry-run
```

Inspect collected SQLite data:

```powershell
.\.venv\Scripts\python.exe scripts\inspect_ai_manju_data.py
```

Run preflight checks:

```powershell
.\.venv\Scripts\python.exe scripts\preflight_ai_manju.py
```

Prepare the browser login session:

```powershell
.\start-cdp-browser.ps1
```

Log in to Xiaohongshu, Douyin, and Kuaishou in the opened browser tabs, then run the one-cycle or loop script.

Start the local WebUI:

```powershell
.\start-webui.ps1
```

Open `http://127.0.0.1:8080` while the WebUI window stays open.

Or start it in the background:

```powershell
.\start-webui-background.ps1
```

Stop the background WebUI:

```powershell
.\stop-webui-background.ps1
```

Verify WebUI routes without opening a browser:

```powershell
.\.venv\Scripts\python.exe scripts\test_webui_local.py
```

## Notes

- SQLite data is stored at `database/sqlite_tables.db`.
- Run logs are appended to `logs/ai_manju_runs.jsonl`; each crawl command also writes a detailed log file under `logs/`.
- The runner uses MediaCrawler's CDP/browser-login configuration. If login or captcha is required, complete it in the opened browser and rerun.
- Each platform command times out after `command_timeout_seconds` so one stuck platform does not block the next scheduled run forever.
- Current upstream schema stores the latest metrics per item. Kuaishou comments do not expose a comment-like field in the local schema.
