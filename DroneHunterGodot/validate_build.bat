@echo off
setlocal enabledelayedexpansion

echo [INFO] Validating Release Prerequisites...

set /a errors=0

if not exist project.godot (
    echo [ERROR] project.godot missing.
    set /a errors+=1
)

if not exist export_presets.cfg (
    echo [ERROR] export_presets.cfg missing.
    set /a errors+=1
) else (
    findstr /C:"name=\"Windows Desktop\"" export_presets.cfg >nul
    if errorlevel 1 (
        echo [ERROR] "Windows Desktop" preset missing in export_presets.cfg.
        set /a errors+=1
    )
)

if not exist scenes\ui\MainMenu.tscn (
    echo [ERROR] Main scene scenes\ui\MainMenu.tscn missing.
    set /a errors+=1
)

rem Check for Boss/Skin references
findstr /s /i /m "BossTitan" scenes\*.tscn scripts\*.gd >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Found BossTitan reference in scenes/scripts. Please ensure it's unreachable.
)

findstr /s /i /m "skinselect" scenes\*.tscn scripts\*.gd >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Found Skin reference in scenes/scripts. Please ensure it's unreachable.
)

if !errors! gtr 0 (
    echo [ERROR] Build validation failed with !errors! errors.
    exit /b 1
)

echo [SUCCESS] Build validation passed.
exit /b 0
