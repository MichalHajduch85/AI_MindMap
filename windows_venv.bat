@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo Enhanced Virtual Environment Runner
echo ========================================

REM Check if script argument is provided
if "%~1"=="" (
    echo Usage: windows_venv.bat ^<script_name^> [args...]
    echo.
    echo Examples:
    echo   windows_venv.bat run_improved.py
    echo.
    pause
    exit /b 1
)

REM Handle special commands
if /i "%~1"=="--status" goto :show_status
if /i "%~1"=="--install" goto :install_requirements
if /i "%~1"=="--help" goto :show_help

REM Load saved configuration if it exists
if exist "last_config.bat" (
    call last_config.bat
    echo Loaded saved configuration
)

REM Function to detect Python installation
:detect_python
echo Checking Python installation...

REM Try Python command in PATH
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python found in PATH
    set PYTHON_CMD=python
    goto :detect_venv
)

REM Try py launcher
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python found via py launcher
    set PYTHON_CMD=py
    goto :detect_venv
)

REM Search common installation paths
echo Searching common Python installation paths...
set SEARCH_PATHS=C:\Python39\python.exe
set SEARCH_PATHS=%SEARCH_PATHS%;C:\Python310\python.exe
set SEARCH_PATHS=%SEARCH_PATHS%;C:\Python311\python.exe
set SEARCH_PATHS=%SEARCH_PATHS%;C:\Python312\python.exe
set SEARCH_PATHS=%SEARCH_PATHS%;C:\Python313\python.exe
set SEARCH_PATHS=%SEARCH_PATHS%;c:\Program Files\Python310\python.exe
set SEARCH_PATHS=%SEARCH_PATHS%;%LOCALAPPDATA%\Programs\Python\Python39\python.exe
set SEARCH_PATHS=%SEARCH_PATHS%;%LOCALAPPDATA%\Programs\Python\Python310\python.exe
set SEARCH_PATHS=%SEARCH_PATHS%;%LOCALAPPDATA%\Programs\Python\Python311\python.exe
set SEARCH_PATHS=%SEARCH_PATHS%;%LOCALAPPDATA%\Programs\Python\Python312\python.exe
set SEARCH_PATHS=%SEARCH_PATHS%;%LOCALAPPDATA%\Programs\Python\Python313\python.exe

for %%p in (%SEARCH_PATHS%) do (
    if exist "%%p" (
        echo Found Python at: %%p
        set PYTHON_CMD=%%p
        goto :detect_venv
    )
)

REM Manual Python path input
:input_python_path
echo.
echo Python not found automatically
echo Please enter the full path to your Python executable
echo Example: C:\Python311\python.exe
echo.
set /p PYTHON_PATH="Python path (or 'exit' to quit): "

if /i "%PYTHON_PATH%"=="exit" (
    echo Exiting...
    pause
    exit /b 1
)

if not exist "%PYTHON_PATH%" (
    echo Path not found: %PYTHON_PATH%
    goto :input_python_path
)

"%PYTHON_PATH%" --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Invalid Python executable
    goto :input_python_path
)

echo Python verified: %PYTHON_PATH%
set PYTHON_CMD=%PYTHON_PATH%

REM Save Python path
echo set PYTHON_CMD=%PYTHON_PATH% > python_path.bat
echo Python path saved

:detect_venv
echo.
echo Detecting virtual environment...

REM Check for existing virtual environments
set VENV_DIR=
set VENV_FOUND=0

for %%v in (venv env .venv mindmap_venv project_env) do (
    if exist "%%v\Scripts\activate.bat" (
        set VENV_DIR=%%v
        set VENV_FOUND=1
        echo Found virtual environment: %%v
        goto :setup_venv
    )
)

REM No virtual environment found
if !VENV_FOUND! equ 0 (
    echo.
    echo No virtual environment found
    echo.
    echo Options:
    echo 1. Create new virtual environment 'venv'
    echo 2. Create virtual environment with custom name
    echo 3. Specify existing virtual environment path
    echo 4. Exit
    echo.
    set /p VENV_CHOICE="Enter choice (1-4): "
    
    if "!VENV_CHOICE!"=="1" (
        set VENV_DIR=venv
        goto :create_venv
    )
    
    if "!VENV_CHOICE!"=="2" (
        set /p VENV_DIR="Enter virtual environment name: "
        if "!VENV_DIR!"=="" set VENV_DIR=venv
        goto :create_venv
    )
    
    if "!VENV_CHOICE!"=="3" (
        goto :input_venv_path
    )
    
    if "!VENV_CHOICE!"=="4" (
        echo Exiting...
        pause
        exit /b 1
    )
    
    echo Invalid choice, creating default 'venv'
    set VENV_DIR=venv
    goto :create_venv
)

:input_venv_path
set /p VENV_DIR="Enter virtual environment path: "
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Virtual environment not found: %VENV_DIR%
    goto :input_venv_path
)
echo Using existing virtual environment: %VENV_DIR%
goto :setup_venv

:create_venv
echo.
echo Creating virtual environment: %VENV_DIR%
"%PYTHON_CMD%" -m venv "%VENV_DIR%"
if %errorlevel% neq 0 (
    echo Failed to create virtual environment
    echo Check Python installation and permissions
    pause
    exit /b 1
)
echo Virtual environment created successfully

:setup_venv
REM Set virtual environment paths
set VENV_PYTHON=%VENV_DIR%\Scripts\python.exe
set VENV_ACTIVATE=%VENV_DIR%\Scripts\activate.bat

REM Verify virtual environment
if not exist "%VENV_PYTHON%" (
    echo Virtual environment Python not found: %VENV_PYTHON%
    echo Virtual environment may be corrupted
    pause
    exit /b 1
)

echo Virtual environment verified: %VENV_DIR%

REM Activate virtual environment if not already active
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call "%VENV_ACTIVATE%"
    if %errorlevel% neq 0 (
        echo Failed to activate virtual environment
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already active: %VIRTUAL_ENV%
)

REM Check and install requirements
:check_requirements
echo.
echo Checking requirements...

REM Test for common dependencies
"%VENV_PYTHON%" -c "import sys; sys.exit(0)" >nul 2>&1
if %errorlevel% neq 0 (
    echo Python test failed in virtual environment
    pause
    exit /b 1
)

REM Check for requirements file
if exist "requirements.txt" (
    echo Requirements file found
    "%VENV_PYTHON%" -c "import pkg_resources; pkg_resources.require(open('requirements.txt').read().splitlines())" >nul 2>&1
    if %errorlevel% neq 0 (
        echo Installing requirements from requirements.txt...
        "%VENV_PYTHON%" -m pip install --upgrade pip
        "%VENV_PYTHON%" -m pip install -r requirements.txt
        if %errorlevel% neq 0 (
            echo Failed to install requirements
            echo Check requirements.txt and network connection
            pause
            exit /b 1
        )
        echo Requirements installed successfully
    ) else (
        echo Requirements already satisfied
    )
) else (
    echo No requirements.txt found
    REM Create basic requirements.txt for common Flask projects
    if not exist "requirements.txt" (
        echo Creating basic requirements.txt...
        (
            echo Flask==2.3.3
            echo Flask-JWT-Extended==4.5.3
            echo Flask-SQLAlchemy==3.0.5
            echo Flask-Migrate==4.0.5
            echo psycopg2-binary==2.9.7
            echo requests==2.31.0
            echo marshmallow==3.20.1
            echo flasgger==0.9.7.1
            echo Werkzeug==2.3.7
            echo python-dotenv==1.0.0
        ) > requirements.txt
        echo Basic requirements.txt created
        goto :check_requirements
    )
)

REM Verify target script exists
if not exist "%~1" (
    echo.
    echo Script not found: %~1
    echo.
    echo Available Python files:
    for %%f in (*.py) do echo   %%f
    echo.
    pause
    exit /b 1
)

REM Display environment information
echo.
echo Environment Information:
echo   Python: %VENV_PYTHON%
echo   Virtual Env: %VENV_DIR%
echo   Script: %~1
echo   Working Dir: %CD%

if exist ".env" (
    echo   Environment file: .env found
) else (
    echo   Environment file: .env not found
)

echo.
echo Running %~1...
echo ========================================
echo.

REM Execute the script with all arguments
"%VENV_PYTHON%" %*
set SCRIPT_EXIT_CODE=%errorlevel%

REM Report execution results
echo.
echo ========================================
if %SCRIPT_EXIT_CODE% equ 0 (
    echo Script completed successfully
) else (
    echo Script failed with exit code: %SCRIPT_EXIT_CODE%
    echo.
    echo Common troubleshooting steps:
    echo - Check requirements: pip install -r requirements.txt
    echo - Verify .env configuration file
    echo - Check for port conflicts
    echo - Review database connections
    echo - Check file permissions
)

REM Save configuration for future runs
echo.
echo Saving configuration...
(
    echo REM Generated configuration
    echo set VENV_DIR=%VENV_DIR%
    if defined PYTHON_CMD echo set PYTHON_CMD=%PYTHON_CMD%
) > last_config.bat

echo Configuration saved to last_config.bat
echo.
pause
goto :eof

REM Special command handlers
:show_status
echo Current Configuration Status:
if exist "last_config.bat" (
    call last_config.bat
    echo   Virtual Environment: %VENV_DIR%
    echo   Python Command: %PYTHON_CMD%
    if exist "%VENV_DIR%\Scripts\python.exe" (
        echo   Status: Virtual environment exists
        "%VENV_DIR%\Scripts\python.exe" --version
    ) else (
        echo   Status: Virtual environment not found
    )
) else (
    echo   No saved configuration found
)
pause
goto :eof

:install_requirements
echo Installing/updating requirements...
if exist "last_config.bat" call last_config.bat
if exist "%VENV_DIR%\Scripts\python.exe" (
    "%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip
    "%VENV_DIR%\Scripts\python.exe" -m pip install -r requirements.txt
) else (
    echo Virtual environment not found
    echo Run the script normally first to create it
)
pause
goto :eof

:show_help
echo Enhanced Virtual Environment Runner
echo.
echo Usage:
echo   windows_venv.bat script_name [arguments]
echo   windows_venv.bat --status
echo   windows_venv.bat --install
echo   windows_venv.bat --help
echo.
echo Commands:
echo   script_name    Run Python script in virtual environment
echo   --status       Show current configuration status
echo   --install      Install/update requirements only
echo   --help         Show this help message
echo.
echo Examples:
echo   windows_venv.bat app.py
echo   windows_venv.bat run_server.py --port 5000
echo   windows_venv.bat --status
echo.
pause
goto :eof

ENDLOCAL