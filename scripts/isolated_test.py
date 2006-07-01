#!/usr/bin/env python
"Run an isolated install, and test it"

import tempfile, os, sys, glob, optparse, warnings

def temp_dir(suffix=""):
    return tempfile.mkdtemp(prefix="testoob_isolated_test_", suffix=suffix)

def remove_dir(d):
    os.system("rm -fr %s" % d)

def python_executable():
    return sys.executable

def extract_archive(archive_file):
    os.system("tar jxf %s" % archive_file)

def archive_dir():
    return glob_one_entry("*")

def install_package(install_dir):
    os.system("%s setup.py install --prefix=%s 1>/dev/null" % (python_executable(), install_dir))

def glob_one_entry(pattern):
    entries = glob.glob(pattern)
    if len(entries) > 1:
        warnings.warn("Expected 1 entry, got %s (%s)" % (len(entries), entries))
    if len(entries) == 0:
        raise RuntimeError("expected 1 entry, got none")
    return entries[0]

class Environment:
    def __init__(self):
        self.originals = {}
        self.save_variable("PATH")
        self.save_variable("PYTHONPATH")

    def save_variable(self, varname):
        self.originals[varname] = os.environ.get(varname)

    def restore_variable(self, varname):
        if self.originals[varname] is None:
            del os.environ[varname]
        else:
            os.environ["varname"] = self.originals[varname]

    def push_path_var(self, varname, newpath):
        print "Adding '%s' to envvar '%s'" % (newpath, varname)
        if varname in os.environ:
            os.environ[varname] = newpath + ":" + os.environ[varname]
        else:
            os.environ[varname] = newpath

    def push_path(self, newpath):
        self.push_path_var("PATH", newpath)

    def push_pythonpath(self, newpath):
        self.push_path_var("PYTHONPATH", newpath)

    def site_packages_dir(self, installdir):
        return glob_one_entry(os.path.join(installdir, "lib", "python*", "site-packages"))
    
    def update_for_install_dir(self, installdir):
        self.push_path(os.path.join(installdir, "bin"))
        self.push_pythonpath(self.site_packages_dir(installdir))

    def restore(self):
        self.restore_variable("PATH")
        self.restore_variable("PYTHONPATH")

def test_archive(archive_file):
    extract_dir = temp_dir("_extract")
    install_dir = temp_dir("_install")
    environment = Environment()

    print "extract_dir:", extract_dir
    print "install_dir:", install_dir
    try:
        os.chdir(extract_dir)

        extract_archive(archive_file)
        
        os.chdir( archive_dir() )

        install_package(install_dir)

        environment.update_for_install_dir(install_dir)

        os.chdir("tests")

        os.system("%s alltests.py" % python_executable())
        
    finally:
        os.chdir("/")
        remove_dir(extract_dir)
        remove_dir(install_dir)
        environment.restore()


def main():
    parser = optparse.OptionParser(usage="%prog [options] [archive-file]")
    parser.add_option("--python", help="The Python executable to use (default: %default)", default="python")

    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error("bad arguments")
    archive = args[0]

    if options.python is None:
        parser.error("missing '--python' argument")
    
    test_archive(archive)

if __name__ == "__main__":
    main()
