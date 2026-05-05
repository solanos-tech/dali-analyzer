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
    $targetPid = [int]$pidText
    $proc = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
    if ($proc) {
        try {
            $proc | Stop-Process -Force -ErrorAction Stop
            Write-Output "Stopped process pid=$targetPid"
        } catch {
            Write-Output "Could not stop pid=$targetPid via Stop-Process: $($_.Exception.Message)"
            try {
                $taskkillOutput = & taskkill /PID $targetPid /T /F 2>&1
                Write-Output "Stopped process tree pid=$targetPid"
                if ($taskkillOutput) {
                    Write-Output ($taskkillOutput | Out-String).Trim()
                }
            } catch {
                Write-Output "Could not stop pid=$targetPid via taskkill: $($_.Exception.Message)"
            }
        }
    } else {
        Write-Output "Process pid=$targetPid already stopped."
    }
}

Remove-Item -Path $pidFile -Force -ErrorAction SilentlyContinue
Write-Output "Runtime stopped."
