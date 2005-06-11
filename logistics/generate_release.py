#! /usr/bin/env python

import re, sys, os

def once(func):
    "A decorator that runs a function only once."
    class Wrapper:
        def __init__(self, func):
            self.func = func
        def __call__(self, *args, **kwargs):
            result = self.func(*args, **kwargs)
            def new_call(*args, **kwargs): return result
            self.__call__ = new_call
            return result
    return Wrapper(func)

def parse_args():
    "parse the cmdline args"
    import optparse
    parser = optparse.OptionParser()

    parser.add_option(
        "--for-keeps", action="store_true",
        help="Actually generate the release (default: make a dry run)")

    parser.add_option(
        "--version",
        help="The release version")

    options, args = parser.parse_args()

    if not options.version: parser.error("no version given")
    version_re=r"^\d(\.\d)+[a-z]?$"
    if not re.match(version_re, options.version):
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
    from os.path import normpath, join, dirname
    return norm_join(dirname(__file__), "..")

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

def svn_info():
    return get_command_output("svn info %s" % root_dir())

def svn_base_url():
    regexp = r"URL: (?P<url>(http|https|svn|file)://\S+)/trunk"
    return re.search(regexp, svn_info()).group("url")

def svn_trunk_url(): return svn_base_url() + "/trunk"
def svn_branches_url(): return svn_base_url() + "/branches"
def svn_tags_url(): return svn_base_url() + "/tags"

@once
def last_branch_revision():
    branch_list = get_command_output("svn list -v %s" % svn_branches_url())
    return get_field(tail(branch_list, 1), 0)

def die(msg):
    raise RuntimeError(msg)

def version():
    return options().version

def svn_up_to_date():
    return len(get_command_output("svn status -u|grep -v '^Status against revision'").strip()) == 0

def replace_string(from_str, to_str, files):
    for file in files:
        run_command("""sed -i 's/%(from_str)s/%(to_str)s/g' %(file)s""" % vars())

def replace_version_string():
    files = [norm_join(root_dir(), file) for file in ("setup.py", "src/testoob/__init__.py")]
    replace_string("__TESTOOB_VERSION__", version(), files)

def create_branch():
    os.chdir(root_dir())
    run_command("svn update")
    if not svn_up_to_date(): die("problem updating with svn")
    update_changelog()

def changelog():
    return norm_join(root_dir(), "docs/CHANGELOG")

def update_changelog():
    temp_changelog = "%s.temp" % changelog()
    run_command("mv %s %s" % (changelog(), temp_changelog))
    run_command("svn log -v -r%s:HEAD %s | cat - %s > %s" %
            (last_branch_revision(), svn_trunk_url(), temp_changelog, changelog()))

create_branch()
