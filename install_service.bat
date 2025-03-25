@echo off
echo ===================================================
echo Windows Alexa Sleep Controller - Service Installer
echo ===================================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: This script must be run as administrator.
    echo Please right-click on this file and select "Run as administrator".
    echo.
    pause
    exit /b 1
)

echo Checking Python installation...
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo Python not found in PATH. Please install Python 3.8 or higher.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Installing required Python packages...
python -m pip install flask flask-login flask-wtf gunicorn waitress pywin32 psutil boto3

echo.
echo Installing Windows service...
python win_service.py install

echo.
echo Starting service...
python win_service.py start

echo.
echo Service installation complete!
echo.
echo You can now access the control panel by visiting:
echo http://localhost:5000
echo.
echo Default login:
echo Username: admin
echo Password: admin
echo.
echo IMPORTANT: For security reasons, please change the default password after login.
echo.
pause