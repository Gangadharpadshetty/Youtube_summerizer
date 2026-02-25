Param(
    [string]$ProjectDir = "."
)

# Resolve paths so the script can be run from any cwd
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
if ([System.IO.Path]::IsPathRooted($ProjectDir)) {
    $TargetDir = $ProjectDir
} else {
    $TargetDir = Join-Path $ScriptDir $ProjectDir
}

Set-Location -Path $TargetDir

$VenvPath = Join-Path $TargetDir ".venv"
if (-not (Test-Path (Join-Path $VenvPath "Scripts\python.exe"))) {
    Write-Error "Virtual environment not found at $VenvPath. Create it with scripts\setup_venv.ps1"
    exit 1
}

$Python = Join-Path $VenvPath "Scripts\python.exe"
Write-Host "Using Python: $Python"

Write-Host "Ensuring pytest is installed in venv..."
& $Python -m pip install --upgrade pip
& $Python -m pip install pytest

Write-Host "Running tests..."
& $Python -m pytest -q tests

exit $LASTEXITCODE
