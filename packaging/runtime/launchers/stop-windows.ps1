$ErrorActionPreference = "Stop"

$rootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$runtimeDir = Join-Path $rootDir ".runtime"
$pidFile = Join-Path $runtimeDir "backend.pid"

Write-Output "Stopping DALI Analyzer runtime..."

if (-not (Test-Path $pidFile)) {
    Write-Output "No PID file found ($pidFile). Nothing to stop."
    exit 0
}

$pidText = (Get-Content -Path $pidFile -Raw).Trim()
if ($pidText) {
    try {
        & taskkill /PID $pidText /T /F | Out-Null
        Write-Output "Stopped process tree pid=$pidText"
    } catch {
        Write-Output "Could not stop pid=${pidText}: $($_.Exception.Message)"
    }
}

Remove-Item -Path $pidFile -Force -ErrorAction SilentlyContinue
Write-Output "Runtime stopped."
