import sys
import src.globals as g
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["PyQt6"],
    "excludes": ["tkinter"],
    "include_files": [
        # "img/",
    ],
    "optimize": 2,
}

# base="Win32GUI" should be used only for Windows GUI app
base = None

# if sys.platform == "win32":
# base = "Win32GUI"

setup(
    name="CheezosVideoCompressor",
    version=g.VERSION,
    description="Compresses videos to any file size",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py", base=base, target_name=f"CheezosVideoCompressor_v{g.VERSION}"
        )
    ],
)
