$ErrorActionPreference = "Stop"

$candidates = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe",
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
  "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
)

$browser = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $browser) {
  throw "Chrome or Edge was not found. Install Chrome/Edge or edit this script with the browser path."
}

$profileDir = Join-Path $PSScriptRoot "browser_data\manual_cdp_profile"
New-Item -ItemType Directory -Force -Path $profileDir | Out-Null

$args = @(
  "--remote-debugging-port=9222",
  "--remote-debugging-address=127.0.0.1",
  "--user-data-dir=$profileDir",
  "--no-first-run",
  "--no-default-browser-check",
  "https://www.xiaohongshu.com",
  "https://www.douyin.com",
  "https://www.kuaishou.com"
)

Start-Process -FilePath $browser -ArgumentList $args
Write-Host "Started browser for MediaCrawler CDP on port 9222."
Write-Host "Profile: $profileDir"
Write-Host "Log in to Xiaohongshu, Douyin, and Kuaishou in the opened browser, then run .\start-ai-manju-once.ps1"
