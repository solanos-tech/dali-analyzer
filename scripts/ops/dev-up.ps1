$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..")).Path
$opsDir = Join-Path $repoRoot ".ops"
$backendPidFile = Join-Path $opsDir "backend.pid"
$frontendPidFile = Join-Path $opsDir "frontend.pid"
$backendLog = Join-Path $opsDir "backend.log"
$backendErrLog = Join-Path $opsDir "backend.err.log"
$frontendLog = Join-Path $opsDir "frontend.log"
$frontendErrLog = Join-Path $opsDir "frontend.err.log"
$backendUrl = "http://127.0.0.1:8000"
$backendHealthUrl = "$backendUrl/health"
$frontendUrl = "http://127.0.0.1:5173"

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

function Cleanup-StartedProcesses {
    Stop-FromPidFile -PidFile $frontendPidFile
    Stop-FromPidFile -PidFile $backendPidFile
}

New-Item -ItemType Directory -Path $opsDir -Force | Out-Null
Write-Output "Starting local dev stack..."
Write-Output "Backend target: $backendUrl (health: $backendHealthUrl)"
Write-Output "Frontend target: $frontendUrl"

if ((Test-Path $backendPidFile) -or (Test-Path $frontendPidFile)) {
    throw "ERROR: existing PID files found. Run .\scripts\ops\dev-down.ps1 first."
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "ERROR: 'uv' not found in PATH."
}
$npmCmd = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $npmCmd) {
    throw "ERROR: 'npm.cmd' not found in PATH."
}

$backendProc = Start-Process `
    -FilePath "uv" `
    -ArgumentList @("run", "--directory", "backend", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000") `
    -WorkingDirectory $repoRoot `
    -RedirectStandardOutput $backendLog `
    -RedirectStandardError $backendErrLog `
    -WindowStyle Hidden `
    -PassThru

$backendProc.Id | Set-Content -Path $backendPidFile -Encoding ascii
Write-Output "Backend process started (pid=$($backendProc.Id)). Waiting for health..."

$backendReady = $false
for ($i = 0; $i -lt 30; $i++) {
    if ($backendProc.HasExited) {
        Get-Content -Path $backendLog -Tail 40 -ErrorAction SilentlyContinue | Out-String | Write-Error
        Cleanup-StartedProcesses
        throw "ERROR: backend process exited before readiness check passed."
    }
    try {
        $resp = Invoke-WebRequest -Uri $backendHealthUrl -UseBasicParsing -TimeoutSec 2
        if ($resp.StatusCode -eq 200) {
            $backendReady = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $backendReady) {
    Get-Content -Path $backendLog -Tail 40 -ErrorAction SilentlyContinue | Out-String | Write-Error
    Cleanup-StartedProcesses
    throw "ERROR: backend failed to become healthy. Check .ops/backend.log"
}

$frontendProc = Start-Process `
    -FilePath $npmCmd.Source `
    -ArgumentList @("run", "dev", "--", "--host", "127.0.0.1", "--port", "5173") `
    -WorkingDirectory (Join-Path $repoRoot "frontend") `
    -RedirectStandardOutput $frontendLog `
    -RedirectStandardError $frontendErrLog `
    -WindowStyle Hidden `
    -PassThru

$frontendProc.Id | Set-Content -Path $frontendPidFile -Encoding ascii
Write-Output "Frontend process started (pid=$($frontendProc.Id)). Waiting for readiness..."

$frontendReady = $false
for ($i = 0; $i -lt 45; $i++) {
    if ($frontendProc.HasExited) {
        Get-Content -Path $frontendLog -Tail 60 -ErrorAction SilentlyContinue | Out-String | Write-Error
        Cleanup-StartedProcesses
        throw "ERROR: frontend process exited before readiness check passed."
    }
    try {
        $resp = Invoke-WebRequest -Uri $frontendUrl -UseBasicParsing -TimeoutSec 2
        if ($resp.StatusCode -eq 200) {
            $frontendReady = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $frontendReady) {
    Get-Content -Path $frontendLog -Tail 60 -ErrorAction SilentlyContinue | Out-String | Write-Error
    Cleanup-StartedProcesses
    throw "ERROR: frontend failed to become ready on http://127.0.0.1:5173"
}

Write-Output ""
Write-Output "Dev stack is READY"
Write-Output "Backend URL: $backendUrl"
Write-Output "Backend health: OK (200) at $backendHealthUrl"
Write-Output "Backend PID: $($backendProc.Id)"
Write-Output "Frontend URL: $frontendUrl"
Write-Output "Frontend health: OK (200) at $frontendUrl"
Write-Output "Frontend PID: $($frontendProc.Id)"
Write-Output "Backend logs: $backendLog"
Write-Output "Backend err logs: $backendErrLog"
Write-Output "Frontend logs: $frontendLog"
Write-Output "Frontend err logs: $frontendErrLog"
