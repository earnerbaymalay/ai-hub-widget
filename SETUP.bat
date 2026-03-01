@echo off
:: AI Hub v5.0 - Setup Script
:: Installs dependencies, creates desktop shortcut, enables autostart

title AI Hub v5 Setup
color 0B
cls

echo ========================================
echo    AI HUB v5.0 - Setup
echo ========================================
echo.

cd /d "%~dp0"

:: Verify v5 widget is present
if not exist "ai_widget_v5.py" (
    echo [ERROR] ai_widget_v5.py not found in current directory!
    echo [INFO]  Run this from the AI-Widget folder.
    pause
    exit /b 1
)

:: Check Python
echo Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install Python 3.8+ from python.org
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [OK] %%i

:: Install dependencies
echo.
echo Installing dependencies ^(psutil, WMI, rich^)...
pip install psutil WMI rich --quiet --upgrade
if %errorlevel% == 0 (
    echo [OK] Dependencies installed
) else (
    echo [WARNING] Some packages may have failed - widget will use fallbacks
)

:: Create desktop shortcut
echo.
echo Creating desktop shortcut...
powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\AI Hub.lnk'); $sc.TargetPath = '%~dp0launch.bat'; $sc.WorkingDirectory = '%~dp0'; $sc.IconLocation = '%SystemRoot%\System32\SHELL32.dll,13'; $sc.Description = 'AI Hub v5'; $sc.Save()"
if %errorlevel% == 0 (
    echo [OK] Desktop shortcut: AI Hub.lnk
) else (
    echo [WARNING] Failed to create desktop shortcut
)

:: Add to startup via autostart.vbs
echo.
echo Adding to Windows startup...
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
copy /Y "%~dp0autostart.vbs" "%STARTUP%\ai-hub-autostart.vbs" >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Autostart enabled ^(ai-hub-autostart.vbs^)
) else (
    echo [WARNING] Could not add to startup folder
)

echo.
echo ========================================
echo    Setup Complete!
echo ========================================
echo.
echo  Launch now:     Double-click 'AI Hub' on Desktop
echo  Or run:         python ai_widget_v5.py
echo.
echo  To disable autostart, delete:
echo  %STARTUP%\ai-hub-autostart.vbs
echo.
pause
