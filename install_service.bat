@echo off
echo Installing Alexa Sleep Service...

REM Get the directory of this batch file
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check Python installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python 3.x.
    pause
    exit /b 1
)

REM Install required packages
echo Installing required Python packages...
pip install flask waitress pywin32 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install required packages.
    pause
    exit /b 1
)

REM Configure service
echo Configuring Windows service...
python "%SCRIPT_DIR%win_service.py" install
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install the service. Please run as administrator.
    pause
    exit /b 1
)

REM Start service
echo Starting service...
python "%SCRIPT_DIR%win_service.py" start
if %ERRORLEVEL% NEQ 0 (
    echo Failed to start the service.
    pause
    exit /b 1
)

echo.
echo Alexa Sleep Service installed successfully!
echo The service will automatically start when Windows boots.
echo.
echo To access the control panel, open a web browser and go to:
echo http://localhost:5000
echo.
echo Default login:
echo Username: admin
echo Password: admin
echo.
echo IMPORTANT: Please change these credentials for security.
echo.

pause
