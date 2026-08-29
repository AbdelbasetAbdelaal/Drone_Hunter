@echo off
setlocal enabledelayedexpansion

if "%GODOT_EXE%"=="" (
    set "GODOT_EXE=godot"
)

"%GODOT_EXE%" --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Godot executable not found at: %GODOT_EXE%
    echo Please set GODOT_EXE environment variable or add godot to PATH.
    exit /b 1
)

echo [INFO] Using Godot executable: %GODOT_EXE%

if exist release (
    echo [INFO] Removing old release directory...
    rmdir /s /q release
)

echo [INFO] Creating release directory...
mkdir release

if not exist project.godot (
    echo [ERROR] project.godot not found.
    exit /b 1
)

if not exist export_presets.cfg (
    echo [ERROR] export_presets.cfg not found.
    exit /b 1
)

echo [INFO] Exporting Windows Release Candidate...
"%GODOT_EXE%" --headless --export-release "Windows Desktop" release\DroneHunter.exe

if errorlevel 1 (
    echo [ERROR] Godot export failed with non-zero exit code.
    exit /b 1
)

if not exist release\DroneHunter.exe (
    echo [ERROR] Export failed! release\DroneHunter.exe not found.
    exit /b 1
)

echo [SUCCESS] Export complete! release\DroneHunter.exe successfully generated.
exit /b 0
