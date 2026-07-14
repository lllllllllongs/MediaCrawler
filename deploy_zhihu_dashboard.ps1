# Stop the server first if running
Write-Host "=== Zhihu Dashboard Deployment ===" -ForegroundColor Cyan
Write-Host "Please ensure the uvicorn server is STOPPED before running this script." -ForegroundColor Yellow
Write-Host ""

$root = "D:\codex\MediaCrawler\MediaCrawler"

# Copy zhihu-dashboard.html to webui
Copy-Item -Path "$root\zhihu-dashboard.html" -Destination "$root\api\webui\zhihu-dashboard.html" -Force
Write-Host "[OK] Copied zhihu-dashboard.html to api/webui/" -ForegroundColor Green

# Copy patched dashboard.py to routers
Copy-Item -Path "$root\dashboard_patched.py" -Destination "$root\api\routers\dashboard.py" -Force
Write-Host "[OK] Replaced api/routers/dashboard.py" -ForegroundColor Green

# Copy patched main.html
Copy-Item -Path "$root\main_patched.html" -Destination "$root\api\webui\main.html" -Force
Write-Host "[OK] Replaced api/webui/main.html" -ForegroundColor Green

# Copy patched douyin-dashboard.html
Copy-Item -Path "$root\douyin-dashboard_patched.html" -Destination "$root\api\webui\douyin-dashboard.html" -Force
Write-Host "[OK] Updated api/webui/douyin-dashboard.html" -ForegroundColor Green

# Copy patched kuaishou-dashboard.html
Copy-Item -Path "$root\kuaishou-dashboard_patched.html" -Destination "$root\api\webui\kuaishou-dashboard.html" -Force
Write-Host "[OK] Updated api/webui/kuaishou-dashboard.html" -ForegroundColor Green

# Copy patched xiaohongshu-dashboard.html
Copy-Item -Path "$root\xiaohongshu-dashboard_patched.html" -Destination "$root\api\webui\xiaohongshu-dashboard.html" -Force
Write-Host "[OK] Updated api/webui/xiaohongshu-dashboard.html" -ForegroundColor Green

Write-Host ""
Write-Host "=== Deployment Complete ===" -ForegroundColor Cyan
Write-Host "You can now restart the server." -ForegroundColor Yellow
