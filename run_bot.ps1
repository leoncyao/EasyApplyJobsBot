# PowerShell script to run the LinkedIn job bot
Clear
Write-Host "Starting LinkedIn Job Bot..." -ForegroundColor Cyan

try {
    # Check if Python is installed
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        throw "Python is not installed or not in PATH"
    }

    # Check if run_bot.py exists
    if (-not (Test-Path "run_bot.py")) {
        throw "run_bot.py not found in current directory"
    }

    # Run the bot with specified options
    Write-Host "Running bot with options: --verbose --skip-login --skip-scraping --retry-failed" -ForegroundColor Yellow
    python run_bot.py --skip-login --skip-scraping --retry-failed

    # Check the exit code
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Bot completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Bot exited with error code: $LASTEXITCODE" -ForegroundColor Red
    }
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
} 