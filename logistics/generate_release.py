#! /usr/bin/env python

import re, sys, os

def parse_args():
    import optparse
    parser = optparse.OptionParser("usage: %prog [options] version")

    parser.add_option(
        "--for-keeps", action="store_true",
        help="Actually generate the release (default: make a dry run)")

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error("no version given")

    version = args[0]
    if not re.match(r"^\d(\.\d)+[a-z]?$", version):
        parser.error("bad version format")

    options.version = version
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
    
def root_dir():
    from os.path import normpath, join, dirname
    return normpath(join(dirname(__file__), ".."))

def get_command_output(cmd):
    try:
        # Cross-platform, requires Python 2.4
        from subprocess import Popen, PIPE
        return Popen(cmd.split(), stdout=PIPE).communicate()[0]
    except ImportError:
        # POSIX-only
        import commands
        return commands.getoutput(cmd)

def run_command(cmd):
    print "* Running '%s'..." % cmd
    if dry_run(): return
    os.system(cmd)

def svn_info():
    return get_command_output("svn info %s" % root_dir())

def svn_url():
    regexp = r"URL: (?P<url>(http|https|svn|file)://\S+)"
    return re.search(regexp, svn_info()).group("url")

def die(msg):
    print>>sys.stderr, msg
    sys.exit(1)

def version():
    return options().version

def create_branch():
    os.chdir(root_dir())
    run_command("svn update")
    

print options()
print root_dir()
print svn_url()
