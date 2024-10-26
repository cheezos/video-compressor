from src import globals as g
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": [
        "PyQt6",
        "requests",
        "os",
        "sys",
        "subprocess",
        "json",
        "platform",
        "pathlib",
        "threading",
    ],
    "excludes": ["tkinter"],
    "optimize": 2,
    "include_files": [("res", "res")],
}

base = "Win32GUI"

executables = [
    Executable(
        "main.py",
        base=base,
        target_name=f"CheezosVideoCompressor_v{g.VERSION}",
        icon="res/icon.ico",
    )
]

setup(
    name="CheezosVideoCompressor",
    version=g.VERSION,
    description="Compress videos to any file size.",
    options={"build_exe": build_exe_options},
    executables=executables,
)
