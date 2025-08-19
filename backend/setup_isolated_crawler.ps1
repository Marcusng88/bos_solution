# PowerShell script to set up isolated crawler environment
Write-Host "Setting up isolated crawler environment..." -ForegroundColor Green
Write-Host ""

# Change to the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Change to the sub-agents directory
Set-Location "app\services\monitoring\agents\sub_agents"

Write-Host "Installing isolated crawler requirements..." -ForegroundColor Yellow
python setup_isolated_crawler.py

Write-Host ""
Write-Host "Setup completed! You can now test the isolated crawler." -ForegroundColor Green
Write-Host ""
Write-Host "To test, run: python test_isolated_crawler.py" -ForegroundColor Cyan
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
