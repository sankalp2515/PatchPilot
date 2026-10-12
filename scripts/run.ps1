# Install and start PatchPilot. No API keys are needed for replay examples.
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'setup.ps1')
& (Join-Path $PSScriptRoot 'start.ps1')
Write-Output 'Open http://127.0.0.1:8017. Choose Open workspace to try a replay example.'
