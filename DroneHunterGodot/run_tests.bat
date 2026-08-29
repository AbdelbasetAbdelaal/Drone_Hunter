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

echo [INFO] Running All Tests...
set /a total=0
set /a passed=0
set /a failed=0

for %%f in (tests\test_*.gd) do (
    echo.
    echo ==================================================
    echo [INFO] Running %%f
    "%GODOT_EXE%" --headless --script %%f
    
    if errorlevel 1 (
        echo [FAIL] %%f failed.
        set /a failed+=1
    ) else (
        echo [PASS] %%f passed.
        set /a passed+=1
    )
    set /a total+=1
)

echo.
echo ==================================================
echo [TEST RESULTS] Total: !total!, Passed: !passed!, Failed: !failed!
echo ==================================================

if !failed! gtr 0 (
    echo [ERROR] Some tests failed.
    exit /b 1
) else (
    echo [SUCCESS] All tests passed!
    exit /b 0
)
