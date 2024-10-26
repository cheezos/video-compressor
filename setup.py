import src.globals as g
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["PyQt6"],
    "excludes": ["tkinter"],
    "optimize": 2,
}

base = "Win32GUI"

setup(
    name="CheezosVideoCompressor",
    version=g.VERSION,
    description="Compress videos to any file size.",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py", base=base, target_name=f"CheezosVideoCompressor_v{g.VERSION}"
        )
    ],
)
