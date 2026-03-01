@echo off
cls
echo.
echo  ========================================
echo    AI Hub Widget - Uninstall
echo  ========================================
echo.
echo  This will remove:
echo  - Widget from startup folder
echo  - Configuration files
echo  - This widget folder
echo.
set /p confirm="Are you sure? (Y/N): "

if /i not "%confirm%"=="Y" goto cancel

echo.
echo Removing from startup...
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\autostart.vbs" >nul 2>&1
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\ai-hub-autostart.vbs" >nul 2>&1

echo Removing configuration...
del "%USERPROFILE%\.ai-hub-v5-config.json" >nul 2>&1
del "%USERPROFILE%\.ai-widget-config.json" >nul 2>&1
del "%USERPROFILE%\.ai-widget-wpf.json" >nul 2>&1

echo.
echo ========================================
echo  Uninstall complete!
echo.
echo  You can now delete this folder:
echo  %~dp0
echo ========================================
pause
goto end

:cancel
echo.
echo Uninstall cancelled.
pause

:end
