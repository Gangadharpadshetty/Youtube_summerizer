Param(
    [string]$ProjectDir = ".",
    [string]$VenvName = ".venv",
    [switch]$InstallRequirements
)

# Resolve script and project paths so the script works from any working directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
if ([System.IO.Path]::IsPathRooted($ProjectDir)) {
    $TargetDir = $ProjectDir
} else {
    $TargetDir = Join-Path $ScriptDir $ProjectDir
}

Set-Location -Path $TargetDir

$VenvPath = Join-Path $TargetDir $VenvName
if (Test-Path $VenvPath) {
    Write-Host "Virtual environment '$VenvName' already exists in $TargetDir"
    Write-Host "To activate run: . $VenvPath\Scripts\Activate.ps1"
    exit 0
}

Write-Host "Creating virtual environment '$VenvName' in $TargetDir..."
python -m venv $VenvPath

if (-not (Test-Path "$VenvPath\Scripts\python.exe")) {
    Write-Error "Failed to create virtual environment. Ensure Python is on PATH and try again."
    exit 1
}

Write-Host "Upgrading pip inside venv..."
& "$VenvPath\Scripts\python.exe" -m pip install --upgrade pip

if (Test-Path (Join-Path $TargetDir "requirements.txt") -PathType Leaf -and $InstallRequirements) {
    Write-Host "Installing requirements from requirements.txt..."
    & "$VenvPath\Scripts\python.exe" -m pip install -r (Join-Path $TargetDir "requirements.txt")
}

Write-Host "Done. To activate the venv for this PowerShell session run:"
Write-Host "    . $VenvPath\Scripts\Activate.ps1"
