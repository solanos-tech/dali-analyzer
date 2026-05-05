$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..")).Path
$opsDir = Join-Path $repoRoot ".ops"
$backendPidFile = Join-Path $opsDir "backend.pid"
$frontendPidFile = Join-Path $opsDir "frontend.pid"

function Stop-ProcessSafe {
    param(
        [int]$TargetPid,
        [string]$Reason
    )

    try {
        $taskkillOutput = & taskkill /PID $TargetPid /T /F 2>&1
        Write-Output "Stopped process tree pid=$TargetPid ($Reason)"
        if ($taskkillOutput) {
            Write-Output ($taskkillOutput | Out-String).Trim()
        }
        return
    } catch {
        # Fallback to Stop-Process when taskkill is unavailable/fails.
    }

    try {
        Stop-Process -Id $TargetPid -Force -ErrorAction Stop
        Write-Output "Stopped process pid=$TargetPid ($Reason)"
    } catch {
        Write-Output "Could not stop pid=$TargetPid ($Reason): $($_.Exception.Message)"
    }
}

function Stop-FromPidFile {
    param(
        [string]$PidFile
    )

    if (-not (Test-Path $PidFile)) {
        Write-Output "No PID file: $PidFile"
        return
    }

    $pidText = (Get-Content -Path $PidFile -Raw).Trim()
    if ($pidText) {
        Stop-ProcessSafe -TargetPid ([int]$pidText) -Reason "from PID file $PidFile"
    } else {
        Write-Output "Empty PID file: $PidFile"
    }

    Remove-Item -Path $PidFile -Force -ErrorAction SilentlyContinue
    Write-Output "Removed PID file: $PidFile"
}

function Stop-ByPort {
    param(
        [int]$Port
    )

    $listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $listeners) {
        Write-Output "No listening process on port $Port"
        return
    }

    $listeners |
        Select-Object -ExpandProperty OwningProcess -Unique |
        ForEach-Object {
            Stop-ProcessSafe -TargetPid $_ -Reason "listening on port $Port"
        }
}

function Stop-OrphanedRepoProcesses {
    param(
        [string]$RootPath
    )

    try {
        $escaped = [regex]::Escape($RootPath)
        $candidates = Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object {
            ($_.Name -in @("python.exe", "node.exe", "uv.exe", "npm.cmd")) -and
            $_.CommandLine -and
            ($_.CommandLine -match $escaped) -and
            (
                ($_.CommandLine -match "app\.main:app") -or
                ($_.CommandLine -match "uvicorn") -or
                ($_.CommandLine -match "vite") -or
                ($_.CommandLine -match "npm-cli\.js")
            )
        }

        if (-not $candidates) {
            Write-Output "No orphaned repo runtime processes found by command line."
            return
        }

        $candidates | ForEach-Object {
            Stop-ProcessSafe -TargetPid $_.ProcessId -Reason "repo runtime command line match"
        }
    } catch {
        Write-Output "Skipping command-line orphan scan: $($_.Exception.Message)"
    }
}

Write-Output "Stopping local dev stack..."
Stop-FromPidFile -PidFile $frontendPidFile
Stop-FromPidFile -PidFile $backendPidFile
Stop-ByPort -Port 5173
Stop-ByPort -Port 8000
Stop-OrphanedRepoProcesses -RootPath $repoRoot

Write-Output "Local dev processes stopped."
