@echo off
rem Double-click to rebuild Parasite Eve after mod changes. Add "launch" to start the game after:
rem   recompile.cmd launch
set LAUNCH=
if /i "%~1"=="launch" set LAUNCH=-Launch
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0recompile.ps1" %LAUNCH%
echo.
pause
