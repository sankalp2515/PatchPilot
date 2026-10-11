$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pidFile = Join-Path $projectRoot '.data\server.pid'
if (-not (Test-Path -LiteralPath $pidFile)) { Write-Output 'No PatchPilot server PID is recorded.'; exit 0 }
$serverProcessId = [int](Get-Content -LiteralPath $pidFile)
$serverProcess = Get-CimInstance Win32_Process -Filter "ProcessId=$serverProcessId"
if ($serverProcess -and $serverProcess.CommandLine -like '*patchpilot.main:app*' -and $serverProcess.ExecutablePath -eq (Join-Path $projectRoot '.venv\Scripts\python.exe')) {
    Stop-Process -Id $serverProcessId
    Write-Output 'PatchPilot server stopped. Run history is retained.'
} elseif ($serverProcess) { throw 'Recorded PID does not belong to this PatchPilot server. It was not stopped.' }
Remove-Item -LiteralPath $pidFile -ErrorAction SilentlyContinue
