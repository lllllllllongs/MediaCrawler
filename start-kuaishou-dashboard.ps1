param([switch]$NoOpen)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$url = "http://127.0.0.1:8080/static/kuaishou-dashboard.html"
try {
  $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2
  $webuiRunning = $response.StatusCode -eq 200
} catch {
  $webuiRunning = $false
}

if ($webuiRunning) {
  Write-Host "WebUI is already running."
} else {
  & (Join-Path $PSScriptRoot "start-webui-background.ps1")
}

Write-Host "Dashboard: $url"
if (-not $NoOpen) {
  Start-Process $url
}
