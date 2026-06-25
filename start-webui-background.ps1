$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
  throw "Python virtual environment not found. Run: uv sync"
}

$logs = Join-Path $PSScriptRoot "logs"
New-Item -ItemType Directory -Force -Path $logs | Out-Null

$pidFile = Join-Path $logs "webui.pid"
if (Test-Path $pidFile) {
  $oldPidText = (Get-Content $pidFile -Raw).Trim()
  if ($oldPidText -match '^\d+$') {
    $oldProcess = Get-Process -Id ([int]$oldPidText) -ErrorAction SilentlyContinue
    if ($oldProcess) {
      Write-Host "WebUI already appears to be running, pid=$oldPidText"
      Write-Host "URL: http://127.0.0.1:8080"
      exit 0
    }
  }
  Remove-Item $pidFile -Force
}

$outLog = Join-Path $logs "webui-8080.out.log"
$errLog = Join-Path $logs "webui-8080.err.log"

$psi = [System.Diagnostics.ProcessStartInfo]::new()
$psi.FileName = $python
$psi.Arguments = "-m uvicorn api.main:app --host 127.0.0.1 --port 8080"
$psi.WorkingDirectory = $PSScriptRoot
$psi.UseShellExecute = $true
$psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
$process = [System.Diagnostics.Process]::Start($psi)

Start-Sleep -Seconds 3
if ($process.HasExited) {
  throw "WebUI exited immediately with code $($process.ExitCode). See $errLog"
}

$listenerPid = $process.Id
$netstat = netstat -ano | Select-String ":8080"
foreach ($line in $netstat) {
  if ($line.Line -match "LISTENING\s+(\d+)$") {
    $listenerPid = [int]$Matches[1]
    break
  }
}

Set-Content -Path $pidFile -Value $listenerPid -Encoding ascii
Write-Host "Started WebUI pid=$listenerPid"
Write-Host "URL: http://127.0.0.1:8080"
