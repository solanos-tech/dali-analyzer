$ErrorActionPreference = "Stop"

$rootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$runtimeDir = Join-Path $rootDir ".runtime"
$bootstrapDir = Join-Path $runtimeDir "bootstrap"
$backendVenv = Join-Path $runtimeDir "backend-venv"
$pidFile = Join-Path $runtimeDir "backend.pid"
$backendLog = Join-Path $runtimeDir "backend.log"
$backendErrLog = Join-Path $runtimeDir "backend.err.log"
$hostAddress = if ($env:DALI_RUNTIME_HOST) { $env:DALI_RUNTIME_HOST } else { "127.0.0.1" }
$port = if ($env:DALI_RUNTIME_PORT) { [int]$env:DALI_RUNTIME_PORT } else { 8000 }
$baseUrl = "http://$hostAddress`:$port"
$healthUrl = "$baseUrl/health"

function Resolve-PythonCommand {
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        return [pscustomobject]@{
            Path = $py.Source
            ExtraArgs = @("-3")
        }
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return [pscustomobject]@{
            Path = $python.Source
            ExtraArgs = @()
        }
    }

    throw "ERROR: Python 3 is required but was not found in PATH."
}

Write-Output "Starting DALI Analyzer runtime..."
Write-Output "Package root: $rootDir"

if (Test-Path $pidFile) {
    throw "ERROR: existing PID file found ($pidFile). Run stop-windows.ps1 first."
}

New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
$pythonCommand = Resolve-PythonCommand

if (-not (Test-Path (Join-Path $bootstrapDir "Scripts\\python.exe"))) {
    Write-Output "Creating bootstrap sandbox..."
    & $pythonCommand.Path @($pythonCommand.ExtraArgs) -m venv $bootstrapDir
}

$bootstrapPython = Join-Path $bootstrapDir "Scripts\\python.exe"
$uvExe = Join-Path $bootstrapDir "Scripts\\uv.exe"

Write-Output "Installing runtime bootstrap dependencies..."
& $bootstrapPython -m pip install --upgrade pip | Out-Null
& $bootstrapPython -m pip install --upgrade uv | Out-Null

Write-Output "Preparing backend sandbox..."
& $uvExe venv $backendVenv | Out-Null
$backendPython = Join-Path $backendVenv "Scripts\\python.exe"
$wheel = Get-ChildItem (Join-Path $rootDir "backend\\wheels\\*.whl") | Select-Object -First 1
if (-not $wheel) {
    throw "ERROR: backend wheel not found in $rootDir\\backend\\wheels."
}
& $uvExe pip install --python $backendPython --upgrade $wheel.FullName | Out-Null

$env:FRONTEND_DIST_DIR = Join-Path $rootDir "frontend\\dist"
$env:RUNTIME_CONFIG_DIR = Join-Path $rootDir "config"
$env:SIM_LOG_DIR = Join-Path $rootDir "logs"
if (-not $env:CORS_ALLOW_ORIGINS) {
    $env:CORS_ALLOW_ORIGINS = "$baseUrl,http://localhost:$port"
}

Write-Output "Launching backend..."
$backendProc = Start-Process `
    -FilePath $backendPython `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", $hostAddress, "--port", "$port") `
    -WorkingDirectory $rootDir `
    -RedirectStandardOutput $backendLog `
    -RedirectStandardError $backendErrLog `
    -WindowStyle Hidden `
    -PassThru

$backendProc.Id | Set-Content -Path $pidFile -Encoding ascii
Write-Output "Backend PID: $($backendProc.Id)"
Write-Output "Waiting for health: $healthUrl"

$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    if ($backendProc.HasExited) {
        Get-Content -Path $backendLog -Tail 80 -ErrorAction SilentlyContinue | Out-String | Write-Error
        Get-Content -Path $backendErrLog -Tail 80 -ErrorAction SilentlyContinue | Out-String | Write-Error
        Remove-Item -Path $pidFile -Force -ErrorAction SilentlyContinue
        throw "ERROR: backend process exited before readiness."
    }

    try {
        $resp = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 2
        if ($resp.StatusCode -eq 200) {
            $ready = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $ready) {
    Get-Content -Path $backendLog -Tail 80 -ErrorAction SilentlyContinue | Out-String | Write-Error
    Get-Content -Path $backendErrLog -Tail 80 -ErrorAction SilentlyContinue | Out-String | Write-Error
    throw "ERROR: backend did not become healthy in time."
}

Write-Output "Runtime is READY"
Write-Output "UI URL: $baseUrl"
Write-Output "Health URL: $healthUrl"
Write-Output "Logs: $backendLog"
Write-Output "Error logs: $backendErrLog"
