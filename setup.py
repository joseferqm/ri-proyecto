import sys  # pip install cx_Freeze
from cx_Freeze import setup, Executable

include_files = ['autorun.inf']
base = None

if sys.platform == "win32":
    base = "Win32GUI"

setup(name="Proyecto_ParteII",
      version="1.0",
      description="Segunda parte del proyecto de RI",
      options={'build_exe': {'include_files': include_files}},
      executables={Executable("main.py", base=base)})

# to run: 'python setup.py build'
