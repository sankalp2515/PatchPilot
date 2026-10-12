$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        uv sync --python 3.12 --extra dev
        if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
    } else {
        if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) { py -3.12 -m venv .venv }
        .venv\Scripts\python.exe -m pip install -r requirements-dev.txt
        if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
    }
    Push-Location web
    try {
        npm ci
        if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' }
        npm run build
        if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
    } finally { Pop-Location }
} finally { Pop-Location }
Write-Output 'Setup complete. Start with: .\scripts\start.ps1'
