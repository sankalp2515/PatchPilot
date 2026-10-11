param([int]$Port = 8017)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$runtimePath = Join-Path $projectRoot '.venv\Scripts\python.exe'
$dataPath = Join-Path $projectRoot '.data'
New-Item -ItemType Directory -Path $dataPath -Force | Out-Null
if (-not (Test-Path -LiteralPath $runtimePath)) { throw 'Run scripts\setup.ps1 first.' }
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'web\dist\index.html'))) { throw 'Build the UI using scripts\setup.ps1 first.' }
try {
    $existing = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/health" -TimeoutSec 2
    if ($existing.app -eq 'PatchPilot') { Write-Output "PatchPilot is already running: http://127.0.0.1:$Port"; exit 0 }
} catch { }
$process = Start-Process -FilePath $runtimePath -ArgumentList @('-m','uvicorn','patchpilot.main:app','--host','127.0.0.1','--port',"$Port") -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $dataPath 'server.stdout.log') -RedirectStandardError (Join-Path $dataPath 'server.stderr.log') -PassThru
$process.Id | Set-Content -LiteralPath (Join-Path $dataPath 'server.pid')
for ($attempt = 0; $attempt -lt 25; $attempt++) {
    Start-Sleep -Milliseconds 400
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/health" -TimeoutSec 2
        if ($health.app -eq 'PatchPilot') { Write-Output "PatchPilot is running: http://127.0.0.1:$Port"; exit 0 }
    } catch { }
    if ($process.HasExited) { throw 'Server exited. Inspect .data\server.stderr.log.' }
}
throw 'Server did not become ready. Inspect .data\server.stderr.log.'
