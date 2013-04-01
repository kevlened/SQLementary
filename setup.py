import sys
import os
from cx_Freeze import setup, Executable  

# Loops through a directory, grabbing relative file path names
def files_in_dir(directory_name):  
    f = []
    for (dirpath, dirname, filenames) in os.walk(directory_name):
        for filename in filenames:
            relpath = os.path.join(dirpath, filename)
            f.append(relpath)
    return f

# Dependencies are automatically detected, but it might need fine tuning.
packages = ["os","flask_sqlalchemy","flask_admin","flask_login","flask_wtf","sqlalchemy.dialects.sqlite","werkzeug","jinja2.ext","email"]
include_files = ['README.txt']
include_files.extend(files_in_dir("static"))
include_files.extend(files_in_dir("templates"))
build_exe_options = {"packages":packages,"include_files":include_files}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
#if sys.platform == "win32":
#    base = "Win32GUI"

setup(  name = "guifoo",
        version = "0.1",
        description = "My GUI application!",
        options = {"build_exe": build_exe_options},
        executables = [Executable("web.py", base=base)])