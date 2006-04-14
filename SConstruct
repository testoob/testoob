#! python

import os, sys
from glob import glob

# SCons extension
def PhonyTarget(alias, action):
    """Returns an alias to a command that performs the
    action.  This is implementated by a Command with a
    nonexistant file target.  This command will run on every
    build, and will never be considered 'up to date'. Acts
    like a 'phony' target in make."""
    from tempfile import mktemp
    from os.path import normpath
    phony_file = normpath(mktemp(prefix="phony_%s_" % alias, dir="."))
    return Alias(alias, Command(phony_file, None, action))

# constants
DISTDIR="dist"
BUILDDIR="build"
WEBGENDIR=os.path.join("web", "output")

# targets:
# [v] clean
# [v] test
# [ ] web
# [v] dist

# helpers

def run_command(cmd):
    print "Running '%s'" % cmd
    os.system(cmd)

def run_commands(commands):
    "run_commands(commands) -> an action that will run the commands"
    def action(target, source, env):
        for command in commands: run_command(command)
    return action

###########
## general
###########

###########
### test
###########
SUITEFILE = "tests/alltests.py"
test_commands = [
    "python%s %s" % (python_version, SUITEFILE)
    for python_version in "2.2", "2.3", "2.4"
]
PhonyTarget("test", action=run_commands(test_commands))

###########
### dist
###########

def create_distribution(distutils_command, extra_options=""):
    python = sys.executable
    distdir = DISTDIR
    cmd = "%(python)s ./setup.py -q %(distutils_command)s --dist-dir=%(distdir)s %(extra_options)s" % vars()
    run_command(cmd)

def create_source_distribution(format):
    create_distribution(distutils_command="sdist", extra_options="--format=" + format)

def create_windows_distribution():
    create_distribution(distutils_command="bdist_wininst")

def create_distfiles(target, source, env):
    Delete("MANIFEST")
    create_source_distribution("gztar")
    create_source_distribution("bztar")
    create_windows_distribution()
    # TODO: webdistfile

PhonyTarget("dist", action=create_distfiles)

###########
### clean
###########

clean_targets = [DISTDIR, BUILDDIR, WEBGENDIR, "MANIFEST"]

PhonyTarget("clean", [Delete(x) for x in clean_targets])

###########
### web
###########

PYTHON_SOURCES=glob("src/testoob/*.py")

builddir=Command(Dir(BUILDDIR), None, Mkdir(BUILDDIR))

# API
APIDIR=os.path.join(BUILDDIR, "api")
apidir = Command(
    Dir(APIDIR), PYTHON_SOURCES,
    "epydoc -o $TARGET --url http://testoob.sourceforge.net -n Testoob -q $SOURCES")
Depends(apidir, builddir)

# $(WEBSITEDIR): $(APIDIR) $(WEBSITE_SOURCES)
# 	cd web && webgen && rm -fr $(WEBSITEDIR) && cp -R output $(WEBSITEDIR) && cp -R $(APIDIR) $(WEBSITEDIR) && chmod -R og+rX $(WEBSITEDIR)

# webgen
WEBGEN_SOURCES = Flatten([
        glob("web/src/*." + ext) for ext in ("page","template","info")
    ])
webgen = Command(Dir(WEBGENDIR), WEBGEN_SOURCES, "cd web && webgen")

# deployed site
WEBSITE_DEPLOYMENT_DIR = "%(HOME)s/public_html/testoob" % os.environ

deploy_site = Command(
    Dir(WEBSITE_DEPLOYMENT_DIR), None,
    [
        Delete(WEBSITE_DEPLOYMENT_DIR),
        Mkdir(WEBSITE_DEPLOYMENT_DIR),
        Copy(WEBGENDIR, WEBSITE_DEPLOYMENT_DIR),
        Copy(APIDIR, WEBSITE_DEPLOYMENT_DIR),
        "chmod -R og+rX $TARGET",
    ]
    )
Depends(deploy_site, webgen)
Depends(deploy_site, apidir)

Alias("web", deploy_site)
