@echo off
echo "Make sure Godot 4.3 is in your PATH to run this."
echo "Running All Tests..."
for %%f in (tests\test_*.gd) do (
    echo Running %%f
    godot --headless --script %%f
)
