$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
  throw "Python virtual environment not found. Run: uv sync"
}

Write-Host "Starting MediaCrawler WebUI at http://127.0.0.1:8080"
Write-Host "Keep this window open while testing. Press Ctrl+C to stop."
& $python -m uvicorn api.main:app --host 127.0.0.1 --port 8080
