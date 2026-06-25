$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
  throw "Python virtual environment not found. Run: uv sync"
}
& $python scripts\ai_manju_runner.py --init-db --once
