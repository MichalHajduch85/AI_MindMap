@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo ----------------------------------------
echo Python Installation Checker
echo ----------------------------------------

REM Check if Python is in PATH
echo Checking if Python is in PATH...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('where python') do (
        echo Python found at: %%i
    )
    python --version
) else (
    echo Python not found in PATH.
)

echo.

REM Check if Python launcher is available
echo Checking for Python launcher (py)...
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python launcher found.
    py --version
    echo Installed Python versions:
    py -0p
) else (
    echo Python launcher not found.
)

echo.

REM Check common installation paths
echo Checking common installation directories...
set COMMON_PATHS=C:\Python39 C:\Python310 C:\Python311 C:\Python312 ^
%LOCALAPPDATA%\Programs\Python\Python39 ^
%LOCALAPPDATA%\Programs\Python\Python310 ^
%LOCALAPPDATA%\Programs\Python\Python311 ^
%LOCALAPPDATA%\Programs\Python\Python312

for %%p in (%COMMON_PATHS%) do (
    if exist "%%p\python.exe" (
        echo Found Python at: %%p\python.exe
        "%%p\python.exe" --version 2>nul
    )
)

echo.
echo Recommendations:
echo - If Python is not found, download it from: https://www.python.org/downloads/
echo - During installation, ensure "Add Python to PATH" is selected.
echo - Python 3.9 or newer is recommended for development.
echo.

pause
ENDLOCAL
