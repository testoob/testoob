import glob, os

def module_name(path):
    return os.path.splitext(os.path.basename(path))[0]

def current_path():
    return os.path.dirname(__file__)

def option_file_glob_pattern():
    return os.path.join(current_path(), "*_option.py")

def module_list():
    return [
        module_name(filename)
        for filename in glob.glob(option_file_glob_pattern())
    ]

def load_options():
    for module in module_list():
        exec "import %s" % module

load_options()
