$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..")).Path
$opsDir = Join-Path $repoRoot ".ops"
$backendPidFile = Join-Path $opsDir "backend.pid"
$frontendPidFile = Join-Path $opsDir "frontend.pid"

function Stop-FromPidFile {
    param(
        [string]$PidFile
    )

    if (-not (Test-Path $PidFile)) {
        return
    }

    $pidText = (Get-Content -Path $PidFile -Raw).Trim()
    if ($pidText) {
        try {
            Stop-Process -Id ([int]$pidText) -ErrorAction SilentlyContinue
        } catch {
            # no-op
        }
    }

    Remove-Item -Path $PidFile -Force -ErrorAction SilentlyContinue
}

Stop-FromPidFile -PidFile $frontendPidFile
Stop-FromPidFile -PidFile $backendPidFile

Write-Output "Local dev processes stopped."
