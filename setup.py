import sys
from cx_Freeze import setup, Executable
import os

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["tkinter", "subprocess", "threading", "re", "socket", "datetime", "os"],
    "excludes": [],
    "include_files": [],
    "optimize": 2,
}

# GUI applications require a different base on Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Network Diagnostic Tool",
    version="1.0.0",
    description="A GUI application for ping and traceroute network diagnostics",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "ping_tool.py", 
            base=base,
            target_name="NetworkDiagnosticTool.exe",
            icon="icon.ico" if os.path.exists("icon.ico") else None
        )
    ]
) 