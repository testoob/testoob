import os, sys, re

script_dir = os.path.dirname(__file__)
base_dir = os.path.abspath(os.path.join(script_dir, ".."))

def die(msg):
    print>>sys.stderr, msg
    sys.exit(1)

def append_to_pathvar(varname, path):
    path_elements = os.environ.get(varname,"").split(os.pathsep)
    os.environ[varname] = os.pathsep.join(path_elements + [path])

append_to_pathvar('PYTHONPATH', os.path.join(base_dir, "src"))
append_to_pathvar('IRONPYTHONPATH', os.path.join(base_dir, "src"))

os.environ["TESTOOB_DEVEL_TEST"] = "1"

class Exec:
    def __init__(self, py_args=None, testoob_extra_args=None):
        self.py_args = py_args or []
        self.testoob_extra_args = testoob_extra_args or []

PYTHON_EXECUTABLES = {
    "2.6" : Exec([r"C:\Python26\python.exe"]),
    "2.5" : Exec([r"C:\Python25\python.exe"]),
    "2.4" : Exec([r"C:\Python24\python.exe"]),
    "2.3" : Exec([r"C:\Python23\python.exe"]),
    "2.2" : Exec([r"C:\Python22\python.exe"], ["--color-mode=never"]), # Python 2.2 pywin32 problems
    "3.1" : Exec([r"C:\Python31\python.exe"]),
    "3.0" : Exec([r"C:\Python30\python.exe"]),
    "2to3" : Exec([r"C:\Python26\python.exe", "-3"]),
    "ipy2.0" : Exec([r"C:\Program Files\IronPython 2.0.2\ipy.exe"]),
    "ipy2.6" : Exec([r"C:\Program Files\IronPython 2.6\ipy.exe"]),
}
DEFAULT_KEY = "2.6"
def get_run_args(args):
    "get_run_args(args) -> py_args(list), testoob_extra_args(list)"
    if len(args) > 0 and args[0] in PYTHON_EXECUTABLES.keys():
        key = args.pop(0) # remove from args list
    else:
        key = DEFAULT_KEY
    if key not in PYTHON_EXECUTABLES:
        die("unknown version '%s', expecting one of %r" % (key, PYTHON_EXECUTABLES.keys()))
    exec_info = PYTHON_EXECUTABLES[key]
    if not os.path.exists(exec_info.py_args[0]):
        die("Can't find python executable '%s'"%exec_info.py_args[0])
    return exec_info.py_args, exec_info.testoob_extra_args + args

print "Can specify python version on the commandline, one of %r" % sorted(PYTHON_EXECUTABLES.keys())
print "Example: '%s 2.6'" % (sys.argv[0])
args = sys.argv[1:]
py_args, testoob_extra_args = get_run_args(args)
testoob_executable = os.path.join(base_dir, "src", "testoob", "testoob")
test_file = os.path.join(base_dir, "tests", "alltests.py")

test_args = py_args + [testoob_executable, test_file, "suite"] + testoob_extra_args
import subprocess
print " ".join(test_args)
subprocess.call(test_args)
