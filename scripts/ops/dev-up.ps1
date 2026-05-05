$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..")).Path
$opsDir = Join-Path $repoRoot ".ops"
$backendPidFile = Join-Path $opsDir "backend.pid"
$frontendPidFile = Join-Path $opsDir "frontend.pid"
$backendLog = Join-Path $opsDir "backend.log"
$frontendLog = Join-Path $opsDir "frontend.log"

New-Item -ItemType Directory -Path $opsDir -Force | Out-Null

if (Test-Path $backendPidFile -or Test-Path $frontendPidFile) {
    throw "ERROR: existing PID files found. Run .\scripts\ops\dev-down.ps1 first."
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "ERROR: 'uv' not found in PATH."
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "ERROR: 'npm' not found in PATH."
}

$backendProc = Start-Process `
    -FilePath "uv" `
    -ArgumentList @("run", "--directory", "backend", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000") `
    -WorkingDirectory $repoRoot `
    -RedirectStandardOutput $backendLog `
    -RedirectStandardError $backendLog `
    -PassThru

$backendProc.Id | Set-Content -Path $backendPidFile -Encoding ascii

$backendReady = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 2
        if ($resp.StatusCode -eq 200) {
            $backendReady = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $backendReady) {
    throw "ERROR: backend failed to become healthy. Check .ops/backend.log"
}

$frontendProc = Start-Process `
    -FilePath "npm" `
    -ArgumentList @("run", "dev", "--", "--host", "127.0.0.1", "--port", "5173") `
    -WorkingDirectory (Join-Path $repoRoot "frontend") `
    -RedirectStandardOutput $frontendLog `
    -RedirectStandardError $frontendLog `
    -PassThru

$frontendProc.Id | Set-Content -Path $frontendPidFile -Encoding ascii

Write-Output "Backend: http://127.0.0.1:8000"
Write-Output "Frontend: http://127.0.0.1:5173"
