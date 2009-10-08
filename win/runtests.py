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

PYTHON_EXECUTABLES = {
    "2.6" : r"C:\Python26\python.exe",
    "2.5" : r"C:\Python25\python.exe",
    "2.4" : r"C:\Python24\python.exe",
    "2.3" : r"C:\Python23\python.exe",
    "2.2" : r"C:\Python22\python.exe",
    "ipy2.6" : r"C:\Program Files\IronPython 2.6\ipy.exe",
}
DEFAULT_KEY = "2.6"
def get_python_executable(args):
    if len(args) > 0 and args[0] in PYTHON_EXECUTABLES.keys():
        key = args.pop(0) # remove from args list
    else:
        key = DEFAULT_KEY
    if key not in PYTHON_EXECUTABLES:
        die("unknown version '%s', expecting one of %r" % (key, PYTHON_EXECUTABLES.keys()))
    result = PYTHON_EXECUTABLES[key]
    if key == "2.2":
        args.append("--color-mode=never") # Python 2.2 pywin32 problems
    if key == "ipy2.6":
        append_to_pathvar('IRONPYTHONPATH', r"C:\Python26\Lib")
    if not os.path.exists(result):
        die("Can't find python executable '%s'"%result)
    return result

print "Can specify python version on the commandline, one of %r" % sorted(PYTHON_EXECUTABLES.keys())
print "Example: '%s 2.6'" % (sys.argv[0])
args = sys.argv[1:]
python_executable = get_python_executable(args)
testoob_executable = os.path.join(base_dir, "src", "testoob", "testoob")
test_file = os.path.join(base_dir, "tests", "alltests.py")

test_args = [python_executable, testoob_executable, test_file, "suite"] + args
import subprocess
subprocess.call(test_args)
