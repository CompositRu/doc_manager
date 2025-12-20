@echo off
chcp 65001 >nul
echo ============================================================
echo DocManager - Windows Firewall Setup
echo ============================================================
echo.
echo This script will add firewall rule for port 8080
echo Requires administrator privileges!
echo.
pause

echo.
echo Adding firewall rule...
netsh advfirewall firewall add rule name="DocManager Port 8080" dir=in action=allow protocol=TCP localport=8080

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo SUCCESS! Firewall rule added.
    echo Server will be accessible from local network on port 8080
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo ERROR! Failed to add rule.
    echo Make sure script is run as administrator:
    echo   Right click -^> Run as administrator
    echo ============================================================
)

echo.
echo Press any key to exit...
pause >nul
