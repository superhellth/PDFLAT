import os
import glob
import importlib

# Get the current directory of __init__.py file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get a list of all Python files in the current directory
module_files = glob.glob(os.path.join(current_dir, "*.py"))

# Exclude the __init__.py file itself
module_files.remove(os.path.abspath(__file__))

# Dynamically import functions from the individual modules
# and add their names to the __all__ list
__all__ = []
for module_file in module_files:
    module_name = os.path.basename(module_file)[:-3]  # Remove the .py extension
    module = importlib.import_module("." + module_name, package="utils.db")
    names = getattr(module, "__all__", None) or [name for name in dir(module) if not name.startswith("_")]
    globals().update({name: getattr(module, name) for name in names})
    __all__.extend(names)
    del module_name, module, names, module_file

del os, glob, importlib, module_files
