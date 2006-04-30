#! /usr/bin/env python

import os, sys

def install_dir():
    return os.path.join(os.environ["HOME"], "inst")

def script_dir():
    from os.path import abspath, normpath, dirname
    return normpath(abspath(dirname(__file__)))
    
def system_information():
    import commands
    return """
System: %s
Python: %s
""".strip() % (commands.getoutput("uname -nsrmpio"), sys.version.replace("\n", " "))

def install():
    print >>sys.stderr, "Installing...",
    os.system("python setup.py -q install --prefix=%s" % install_dir())
    print >>sys.stderr, "done."

def update_python_path():
    from glob import glob
    from os.path import join
    directories = [join(dir, "site-packages") for dir in glob(join(install_dir(), "lib", "*"))]
    os.environ.setdefault("PYTHONPATH", "")
    os.environ["PYTHONPATH"] += ":" + (":".join( directories ))

def run_tests():
    executable = os.path.join(install_dir(), "bin", "testoob")
    return os.system("%(executable)s tests/alltests.py suite" % vars())

def cleanup():
    os.system("rm -fr %s" + install_dir())

def main():
    os.chdir( script_dir() )

    print >>sys.stderr, "Testoob installation test"
    print >>sys.stderr, system_information()

    install()
    update_python_path()
    return run_tests()

if __name__ == "__main__":
    try:
        rc = main()
    finally:
        cleanup()
    sys.exit(rc)
