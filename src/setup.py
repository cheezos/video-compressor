from cx_Freeze import setup, Executable
from pathlib import Path
import os

icon_path: str = Path(os.getcwd())
icon_path = f"{icon_path.parent.absolute()}/icon.ico"

build_exe_options = {
    "excludes": ["tkinter"],
    "zip_include_packages": "PyQt5",
    "optimize": 2,
}

setup(
    name="Big Slime Video Compressor",
    version="1.2.3",
    description="A video compressor created in Python",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            target_name="Big Slime Video Compressor v1.2.3.exe",
            base="Win32GUI",
            icon=icon_path,
        )
    ],
)
