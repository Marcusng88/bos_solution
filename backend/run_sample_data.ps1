#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Generate sample ROI data for beautiful dashboard visualization
    
.DESCRIPTION
    This script populates the roi_metrics table with realistic sample data
    for YouTube, Instagram, and Facebook platforms to create professional-looking graphs in the ROI dashboard.
#>

param(
    [switch]$Force,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
🎯 ROI Sample Data Generator

This script creates comprehensive sample data for the ROI dashboard including:
• ROI metrics across YouTube, Instagram, and Facebook platforms
• 90 days of historical data for beautiful trend visualization
• Platform-specific performance patterns and realistic metrics

Usage:
    .\run_sample_data.ps1 [-Force] [-Help]

Parameters:
    -Force    Skip confirmation prompts
    -Help     Show this help message

Requirements:
    • Python 3.8+
    • Supabase connection configured
    • Backend environment variables set
    • roi_metrics table must exist

"@ -ForegroundColor Cyan
    exit 0
}

# Set console colors and formatting
$Host.UI.RawUI.WindowTitle = "ROI Sample Data Generator"
Write-Host "🎯 Starting ROI Sample Data Generation..." -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "populate_roi_sample_data.py")) {
    Write-Host "❌ Error: populate_roi_sample_data.py not found in current directory" -ForegroundColor Red
    Write-Host "Please run this script from the backend directory" -ForegroundColor Yellow
    exit 1
}

# Check Python installation
Write-Host "📋 Checking Python installation..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again" -ForegroundColor Yellow
    exit 1
}

# Check if environment is set up
Write-Host "🔧 Checking environment setup..." -ForegroundColor Cyan
if (-not (Test-Path ".env") -and -not $Force) {
    Write-Host "⚠️  Warning: .env file not found" -ForegroundColor Yellow
    Write-Host "Make sure your Supabase environment variables are configured" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Host "❌ Aborted by user" -ForegroundColor Red
        exit 1
    }
}

# Confirmation prompt
if (-not $Force) {
    Write-Host ""
    Write-Host "📊 This will create sample data including:" -ForegroundColor Cyan
    Write-Host "   • ~800-1200 ROI metrics records (90 days)" -ForegroundColor White
    Write-Host "   • Platforms: YouTube, Instagram, Facebook only" -ForegroundColor White
    Write-Host "   • Target table: roi_metrics only" -ForegroundColor White
    Write-Host "   • 3 content types and 6 content categories" -ForegroundColor White
    Write-Host ""
    $confirm = Read-Host "Continue with sample data generation? (y/N)"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "❌ Aborted by user" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🚀 Running sample data generation script..." -ForegroundColor Green
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
Write-Host ""

# Run the Python script
try {
    $startTime = Get-Date
    python populate_roi_sample_data.py
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Gray
    Write-Host "🎉 Sample data generation completed successfully!" -ForegroundColor Green
    Write-Host "⏱️  Duration: $($duration.ToString('mm\:ss'))" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✨ Your ROI dashboard should now display beautiful, professional graphs!" -ForegroundColor Green
    Write-Host "🚀 You can now visit the ROI dashboard to see the enhanced visualizations." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "💡 Platform-specific patterns:" -ForegroundColor Yellow
    Write-Host "   • YouTube: Higher views, moderate engagement, high revenue potential" -ForegroundColor White
    Write-Host "   • Instagram: High engagement rates, strong visual content performance" -ForegroundColor White
    Write-Host "   • Facebook: Balanced performance across all metrics" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Tips:" -ForegroundColor Yellow
    Write-Host "   • Try different time ranges (7d, 30d, 90d, 1y) in the dashboard" -ForegroundColor White
    Write-Host "   • Explore different tabs (Overview, Revenue, Costs, Profitability, Channels)" -ForegroundColor White
    Write-Host "   • The data includes realistic seasonal variations and platform-specific patterns" -ForegroundColor White
    
} catch {
    Write-Host ""
    Write-Host "❌ Error during sample data generation:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   • Check your Supabase connection settings" -ForegroundColor White
    Write-Host "   • Ensure all required environment variables are set" -ForegroundColor White
    Write-Host "   • Verify the roi_metrics table exists and is accessible" -ForegroundColor White
    exit 1
}

Write-Host ""
Read-Host "Press Enter to continue..."
