#!/usr/bin/env python
"Run an isolated install, and test it"

import tempfile, os, sys, glob, optparse, warnings

def absnorm(path):
    return os.path.normpath(os.path.abspath(path))

def absjoin(*args):
    return absnorm(os.path.join(*args))

def temp_dir(suffix=""):
    return tempfile.mkdtemp(prefix="testoob_isolated_test_", suffix=suffix)

def extract_archive(archive_file):
    suffix_rules = {
        ".tar.gz" : "tar -zxf %s",
        ".tar.bz2" : "tar -jxf %s",
        ".zip" : "unzip %s",
    }
    for suffix, rule in suffix_rules.items():
        if archive_file.endswith(suffix):
            system(rule % archive_file)
            return
    raise RuntimeError("Unknown file extenstion for %s" % os.path.basename(archive_file))

def install_package(install_dir, python):
    system("%s setup.py install --prefix=%s 1>/dev/null" % (python, install_dir))

def glob_one_entry(pattern):
    entries = glob.glob(pattern)
    if len(entries) > 1:
        warnings.warn("Expected 1 entry, got %s (%s)" % (len(entries), entries))
    if len(entries) == 0:
        raise RuntimeError("expected 1 entry, got none")
    return entries[0]

def chdir(dir):
    print "chdir(%r)" % dir
    return os.chdir(dir)

def system(cmd):
    print "system(%r)" % cmd
    return os.system(cmd)

class TempDirs:
    def __init__(self, prefix="testoob_isolated_test_"):
        self.dirs = []
        self.prefix = prefix
    def create(self, description):
        result = tempfile.mkdtemp(prefix=self.prefix, suffix="_" + description)
        self.dirs.append(result)
        print "%s directory: %s" % (description, result)
        return result
    def cleanup(self):
        chdir("/")
        for dir in self.dirs:
            self._remove_dir(dir)
    def _remove_dir(self, dir):
        system("rm -fr %s" % dir)

temp_dirs = TempDirs()

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
            os.environ[varname] = newpath + os.pathsep + os.environ[varname]
        else:
            os.environ[varname] = newpath

    def push_path(self, newpath):
        self.push_path_var("PATH", newpath)

    def push_pythonpath(self, newpath):
        self.push_path_var("PYTHONPATH", newpath)

    def site_packages_dir(self, installdir):
        return glob_one_entry(absjoin(installdir, "lib", "python*", "site-packages"))
    
    def update_for_install_dir(self, installdir):
        self.push_path(absjoin(installdir, "bin"))
        self.push_pythonpath(self.site_packages_dir(installdir))

    def restore(self):
        self.restore_variable("PATH")
        self.restore_variable("PYTHONPATH")

def test_installation(install_dir, tests_file, python):
    environment = Environment()
    try:
        environment.update_for_install_dir(install_dir)
        system("%s %s" % (python, tests_file))
    finally:
        environment.restore()

def test_source(source_dir, python):
    install_dir = temp_dirs.create("install")
    chdir(source_dir)
    install_package(install_dir, python=python)
    test_installation(
        install_dir,
        tests_file=absjoin(source_dir, "tests", "alltests.py"),
        python=python
    )
        
def test_archive(archive_file, python):
    extract_dir = temp_dirs.create("extract")
    chdir(extract_dir)
    extract_archive(archive_file)
    archive_dir = absnorm(glob_one_entry("*"))
    test_source( source_dir = archive_dir, python = python )

def main():
    parser = optparse.OptionParser(usage="%prog [options] [archive-file]")
    parser.add_option("--python", help="The Python executable to use (default: '%default')", default="python")
    parser.add_option("--archive", help="The archive to extract and test (default: None)")
    parser.add_option("--source-dir", help="The source directory to install from (default: '%default')", default=".")

    try:

        options, args = parser.parse_args()

        if len(args) != 0:
            parser.error("bad arguments")

        if options.archive:
            test_archive( absnorm(options.archive), options.python )
        
        else:
            test_source( absnorm(options.source_dir), options.python )
    finally:
        temp_dirs.cleanup()

if __name__ == "__main__":
    main()
