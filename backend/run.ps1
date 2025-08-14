# PowerShell script to run the BOS Solution backend server
# Usage: .\run.ps1

Write-Host "🚀 Starting BOS Solution Backend Server..." -ForegroundColor Green
Write-Host ""

try {
    python run.py
}
catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Write-Host "Press any key to continue..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
