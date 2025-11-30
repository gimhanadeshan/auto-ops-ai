# Wrapper to allow launching the repo run.ps1 when executed from the backend folder
# This script finds the repository root (parent folder) and invokes the root run.ps1

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
$rootRun = Join-Path $repoRoot "run.ps1"
if (-not (Test-Path $rootRun)) {
    Write-Host "Could not find run.ps1 at repository root: $rootRun" -ForegroundColor Red
    exit 1
}

Write-Host "Invoking repository run script: $rootRun" -ForegroundColor Cyan
& $rootRun @Args
