@echo off
REM Pragati Bharati Document Intelligence Workbench Launcher
echo ======================================================================
echo Starting Pragati Bharati Service via .venv
echo ======================================================================

if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0run.py" %*
) else (
    python "%~dp0run.py" %*
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Service stopped with exit code %ERRORLEVEL%.
    pause
)
