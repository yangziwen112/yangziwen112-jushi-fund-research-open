param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    $env:PYTHONPATH = "src"
    & $Python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw "unit tests failed" }
    & $Python -m compileall -q src
    if ($LASTEXITCODE -ne 0) { throw "compile check failed" }
    git diff --check
    if ($LASTEXITCODE -ne 0) { throw "whitespace check failed" }
    Write-Host "Daily maintenance check passed. No files were changed by this script."
} finally {
    Pop-Location
}
