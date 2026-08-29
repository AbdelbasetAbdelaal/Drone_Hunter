@echo off
echo "Make sure Godot 4.3 is in your PATH."
echo "Cleaning release directory..."
if exist release rmdir /s /q release
mkdir release

echo "Exporting Windows Release Candidate..."
godot --headless --export-release "Windows Desktop" release/DroneHunter.exe

echo "Export Complete."
