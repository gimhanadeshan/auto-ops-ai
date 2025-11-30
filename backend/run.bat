@echo off
REM Wrapper to invoke repo-root run.bat (or run.ps1 if preferred)
SET SCRIPT_DIR=%~dp0
PUSHD %SCRIPT_DIR%..
IF EXIST run.bat (
  call run.bat %*
) ELSE IF EXIST run.ps1 (
  powershell -ExecutionPolicy Bypass -File run.ps1 %*
) ELSE (
  echo Could not find run.bat or run.ps1 in repository root.
  POPD
  exit /b 1
)
POPD
