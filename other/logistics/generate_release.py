#! /usr/bin/env python

import re, sys, os, warnings
import pysvn

def _log(s):
    print >>sys.stderr, "* " + str(s)

def _args_string(*args, **kwargs):
    args_strings = [repr(x) for x in args]
    kwargs_strings = ["%s=%r" % item for item in kwargs.items()]
    return ", ".join(args_strings + kwargs_strings)

def log_call(callable, *args, **kwargs):
    try:
        name = callable.func_name
    except AttributeError:
        name = str(callable)
    _log("Calling %s(%s)" % (name, _args_string(*args, **kwargs)))
    callable(*args, **kwargs)

class LoggingProxy(object):
    def __init__(self, object, log=_log, name=None, dry_run=False):
        self.__object = object
        self.__log = log
        self.__name = name
        self.__prefix = name and name + "." or ""
        self.__dry_run = False
        self._init_done = True

    def __getattr__(self, name):
        result = getattr(self.__object, name)
        if callable(result):
            return LoggingProxy(result, name = self.__prefix + name)
        self.__log('attr %r accessed' % (self.__prefix + name))

    def __call__(self, *args, **kwargs):
        self.__log("calling %s(%s)" % (self.__name, _args_string(*args, **kwargs)))
        if self.__dry_run: return
        return self.__object(*args, **kwargs)

    def __setattr__(self, name, value):
        if not hasattr(self, "_init_done") or not getattr(self, "_init_done"):
            self.__dict__[name] = value
        else:
            self.__log('setting %r to %r' % (name, value))
            setattr(self.__object, name, value)

def svnclient():
    return LoggingProxy(pysvn.Client(), dry_run=dry_run())

def once(func):
    """A decorator that runs a function only once.
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/425445"""
    def save_result(*args, **kwargs):
        result = func(*args, **kwargs)
        func_list[0] = lambda *args, **kwargs: result
        return result
    func_list = [save_result]
    return lambda *args, **kwargs: func_list[0](*args, **kwargs)

def parse_args():
    "parse the cmdline args"
    import optparse
    parser = optparse.OptionParser()

    parser.add_option(
        "--root-dir",
        help = "the project's root dir")

    parser.add_option(
        "--for-keeps", action="store_true",
        help="actually modify the repository")

    parser.add_option(
        "--release", metavar="VERSION",
        help="generate a release")

    parser.add_option(
        "--update-changelog", action="store_true",
        help="update the changelog")

    parser.add_option("--test", action="store_true",
            help="For testing the script")

    options, args = parser.parse_args()

    if not options.root_dir: parser.error("root dir missing")

    if options.release:
        version_re=r"^\d(\.\d+)+[a-z]?$"
        if not re.match(version_re, options.release):
            parser.error("bad version format, should match " + version_re)

    return options

_options_ = None
def options():
    "single instance of options"
    global _options_
    if _options_ is None:
        _options_ = parse_args()
    return _options_

def dry_run():
    return not options().for_keeps

def norm_join(*args):
    "os.join, then os.normpath"
    from os.path import normpath, join
    return normpath(join(*args))

def root_dir():
    "the project's root dir"
    return options().root_dir

def get_command_output(cmd):
    import commands
    return commands.getoutput(cmd)

def run_command(cmd):
    _log("Running '%s'..." % cmd)
    sys.stdout.flush()
    if dry_run(): return
    os.system(cmd)

def tail(string, num_lines):
    "tail(string, num_lines) -> the last num_lines of string"
    return "\n".join(string.splitlines()[-num_lines:])

@once
def base_url():
    return svnclient().info(root_dir()).repos

def branch_name(): return "RB-%s" % version()
def trunk_url(): return base_url() + "/trunk"
def branches_url(): return base_url() + "/branches"
def release_branch_url(): return branches_url() + "/%s" % branch_name()
def release_tag_url(): return base_url() + "/tags/REL-%s" % version()

@once
def last_branch_revision():
    entries = [
        e
        for e in svnclient().ls(branches_url())
        if os.path.basename(e['name']).startswith("RB")
    ]

    if len(entries) == 0:
        # no release branches, last revision is the first
        return 0
    
    return entries[-1]["created_rev"].number

def die(msg):
    raise RuntimeError(msg)

def version():
    return options().release

def up_to_date(path):
    def _status_kind_up_to_date(status_kind):
        from pysvn import wc_status_kind as sk
        return status_kind in (
            sk.normal,
            sk.ignored,
            sk.none,
            sk.external,
        )
    status_list = svnclient().status(root_dir(), update=True)
    for status in status_list:
        for s in (status.prop_status, status.text_status, status.repos_prop_status, status.repos_text_status):
            if not _status_kind_up_to_date(s):
                if s == pysvn.wc_status_kind.unversioned:
                    warnings.warn("%s is unversioned" % status.path)
                    continue
                return False
    return True

def replace_string(from_str, to_str, file):
    if not os.path.exists(file):
        warnings.warn("File '%s' not found, skipping" % file)
        return
    f = open(file)
    try: content = f.read()
    finally: f.close()
    os.rename(file, file + ".bak")
    f = open(file, "w")
    try: f.write(content)
    finally: f.close()
    os.unlink(file + ".bak")

def replace_version_string():
    files = [norm_join(root_dir(), file) for file in ("Makefile", "setup.py", "src/testoob/__init__.py")]
    for file in files:
        replace_string("__TESTOOB_VERSION__", version(), file)

def svn_copy(source, target, log_message):
    _log("svn copy: src=%s, target=%s, log=%r" % (source, target, log_message))
    sys.stdout.flush()
    if dry_run(): return

    client = pysvn.Client()
    client.callback_get_log_message = lambda: (True, log_message)
    client.copy( source, target )

def branch_release():
    svnclient().update( root_dir() )

    if not up_to_date(root_dir()): die("svn tree isn't up-to-date!")

    svn_copy( trunk_url(), release_branch_url(), "Branching release %s" % version() )

def tag_release():
    svn_copy( release_branch_url(), release_tag_url(), version() )

def changelog():
    return norm_join(root_dir(), "docs/CHANGELOG")

def update_changelog():
    temp_changelog = "%s.temp" % changelog()
    log_call(os.rename, changelog(), temp_changelog)
    run_command("svn log -v -r%s:HEAD %s | cat - %s > %s" %
            (last_branch_revision(), trunk_url(), temp_changelog, changelog()))
    log_call(os.unlink, temp_changelog)

def switch_to_branch():
    svnclient().switch( root_dir(), release_branch_url() )

def switch_to_trunk():
    svnclient().switch( root_dir(), trunk_url() )

def commit(msg):
    svnclient().checkin( root_dir(), msg )

def create_release_branch():
    branch_release()
    switch_to_branch()
    replace_version_string()
    commit("updated version string for release %s" % version())
    tag_release()
    switch_to_trunk()

def release_dir(): return "/tmp"

def distfiles():
    basenames = [
        x % version() for x in (
            "testoob-%s.tar.gz",
            "testoob-%s.tar.bz2",
            "testoob-%s.win32.exe",
        )
    ]

    from os.path import join
    return [join(release_dir(), basename) for basename in basenames]

def create_distribution():
    import tempfile
    dir = tempfile.mkdtemp(suffix=".generate_release")
    original_dir = os.getcwd()
    try:
        os.chdir(dir)
        svnclient().checkout( release_branch_url(), branch_name() )
        os.chdir(branch_name())
        run_command("make distfiles")
        run_command("mkdir -p %s" % release_dir())
        run_command("cp dist/* %s" % release_dir())
    finally:
        os.chdir(original_dir)
        run_command("rm -fr %s" % dir)

def upload_to_sourceforge():
    run_command("ncftpput upload.sourceforge.net incoming " + " ".join(distfiles()))

def perform_release():
    create_release_branch()
    create_distribution()
    upload_to_sourceforge()

def main():
    if options().test:
        print base_url()
        print trunk_url()
        print branches_url()

        import time
        start = time.time()
        print last_branch_revision()
        print "Time for query:", time.time() - start

        return

    if options().update_changelog:
        update_changelog()

    elif options().release:
        perform_release()

    else:
        print >>sys.stderr, "Bad arguments, run with '-h' for usage"

if __name__ == "__main__":
    main()
