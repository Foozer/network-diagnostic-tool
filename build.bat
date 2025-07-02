@echo off
echo Building Network Diagnostic Tool...
echo.

echo Installing build dependencies...
pip install -r build_requirements.txt

echo.
echo Building executable with PyInstaller...
if exist icon.ico (
    pyinstaller --onefile --windowed --name "NetworkDiagnosticTool" --icon=icon.ico ping_tool.py
) else (
    pyinstaller --onefile --windowed --name "NetworkDiagnosticTool" ping_tool.py
)

echo.
echo Copying additional files to dist directory...
if exist icon.ico (
    copy icon.ico dist\
    echo Icon file copied to dist directory.
)

echo.
echo Build complete! Check the dist/ directory for the executable.
pause 