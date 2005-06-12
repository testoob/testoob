#! /usr/bin/env python

import re, sys, os

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

    options, args = parser.parse_args()

    if not options.root_dir: parser.error("root dir missing")

    if options.release:
        version_re=r"^\d(\.\d)+[a-z]?$"
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
    print "* Running '%s'..." % cmd
    if dry_run(): return
    os.system(cmd)

def tail(string, num_lines):
    "tail(string, num_lines) -> the last num_lines of string"
    return "\n".join(string.splitlines()[-num_lines:])

def get_field(line, field_index):
    "get_field(line, field_index): the field in the index of the line (starts with 0)"
    return line.split()[field_index]

@once
def svn_info():
    return get_command_output("svn info %s" % root_dir())

def base_url():
    regexp = r"URL: (?P<url>(http|https|svn|file)://\S+)/trunk"
    return re.search(regexp, svn_info()).group("url")

def branch_name(): return "RB-%s" % version()
def trunk_url(): return base_url() + "/trunk"
def branches_url(): return base_url() + "/branches"
def release_branch_url(): return branches_url() + "/%s" % branch_name()

@once
def last_branch_revision():
    branch_list = get_command_output("svn list -v %s|grep ' RB-'" % branches_url())
    return get_field(tail(branch_list, 1), 0)

def die(msg):
    raise RuntimeError(msg)

def version():
    return options().release

def up_to_date():
    return len(get_command_output("svn status -u|grep -v '^Status against revision'").strip()) == 0

def replace_string(from_str, to_str, files):
    for file in files:
        run_command("""sed -i "" 's/%(from_str)s/%(to_str)s/g' %(file)s""" % vars())

def replace_version_string():
    files = [norm_join(root_dir(), file) for file in ("setup.py", "src/testoob/__init__.py")]
    replace_string("__TESTOOB_VERSION__", version(), files)

def branch_release():
    os.chdir(root_dir())
    run_command("svn update")
    if not up_to_date(): die("svn tree isn't up-to-date!")
    run_command("svn copy %s %s -m 'Branching release %s'" % (trunk_url(), release_branch_url(), version()))

def changelog():
    return norm_join(root_dir(), "docs/CHANGELOG")

def update_changelog():
    temp_changelog = "%s.temp" % changelog()
    run_command("mv %s %s" % (changelog(), temp_changelog))
    run_command("svn log -v -r%s:HEAD %s | cat - %s > %s" %
            (last_branch_revision(), trunk_url(), temp_changelog, changelog()))
    run_command("rm -f %s" % temp_changelog)

def switch_to_branch():
    run_command("svn switch %s %s" % (release_branch_url(), root_dir()))

def switch_to_trunk():
    run_command("svn switch %s %s" % (trunk_url(), root_dir()))

def commit(msg):
    run_command("svn commit %s -m '%s'" % (root_dir(), msg))

def create_release_branch():
    branch_release()
    switch_to_branch()
    replace_version_string()
    commit("updated version string")
    switch_to_trunk()

def release_dir(): return "/tmp"
def distfile(): return release_dir() + "/testoob-%s.tar.bz2" % version()

def create_distribution():
    import tempfile
    dir = tempfile.mkdtemp(suffix=".generate_release")
    try:
        os.chdir(dir)
        run_command("svn co -q %s %s" % (release_branch_url(), branch_name()))
        os.chdir(branch_name())
        run_command("gmake dist")
        run_command("mkdir -p %s" % release_dir())
        run_command("cp dist/* %s" % release_dir())
    finally:
        os.chdir("/")
        run_command("rm -fr %s" % dir)

def run_tests():
    pass # TODO

def upload_to_sourceforge():
    run_command("ncftpput upload.sourceforge.net incoming %s" % distfile())

def remove_distribution():
    os.unlink(distfile())

def perform_release():
    create_release_branch()
    create_distribution()
    run_tests()
    upload_to_sourceforge()
    remove_distribution()

if options().update_changelog:
    update_changelog()

elif options().release:
    perform_release()

else:
    print >>sys.stderr, "Bad arguments, run with '-h' for usage"
