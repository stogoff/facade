import sys
# noinspection PyUnresolvedReferences
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

build_options = {
    "includes":
        ["math"],
    "include_files":
        ["main.ui", "icon.png", "img.png"]
}

setup(
    name="facade",
    version="0.1",
    description="my GUI application",
    options={"build_exe": build_options},
    executables=[Executable("facade.py", base=base)],
    requires=['xlrd']
)
