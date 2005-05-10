#!/usr/bin/python
"""
Automatic backups of projects hosted at OpenSVN.

Copyright (c) 2005, Ori Peleg
All rights reserved.

Distributed under the terms of the BSD license,
http://www.opensource.org/licenses/bsd-license.php

Uses module ClientForm from http://wwwsearch.sourceforge.net/ClientForm/
"""

class LoginFailedError(RuntimeError): pass

class OpenSVNBackups:
    "Automatic backups of projects hosted at OpenSVN."

    def __init__(self, projectname, options):
        "__init__(projectname) -> initialize a backups object for the project"
        self.projectname = projectname
        self.options = options
        self.opener = self.new_opener()

    def login(self, password):
        "login(password) -> log into OpenSVN"
        if self.options.dry_run: return
        from ClientForm import ParseResponse
        forms = ParseResponse(self.urlopen("https://opensvn.csie.org"))
        form = self.choose_form("login", forms)
        form["project"] = self.projectname
        form["password"] = password

        result = self.urlopen(form.click()).read()
        if result == 'login failed':
            raise LoginFailedError()

    def backup_svn(self, r1, r2):
        "backup_svn(r1, r2) -> backup subversion repository from r1 to r2"
        filename = "%s-svn-%s.gz" % (self.projectname, self.options.suffix)
        url = "https://opensvn.csie.org/getbackup.pl/" + filename
        self.save_url(url, filename)

    def backup_trac(self):
        "backup_trac() -> backup trac repository"
        filename = "%s-trac-%s.tgz" % (self.projectname, self.options.suffix)
        url = "https://opensvn.csie.org/getbackup.pl/%s?action=trac" % filename
        self.save_url(url, filename)

    # helper methods

    def urlopen(self, url):
        return self.opener.open(url)

    def new_opener(self):
        from cookielib import CookieJar
        from urllib2 import build_opener, HTTPCookieProcessor
        return build_opener(HTTPCookieProcessor(CookieJar()))

    def choose_form(self, action, forms):
        for form in forms:
            if form["action"] == action:
                return form

    def save_url(self, url, filename):
        if self.options.dry_run: return
        file(filename, "wb").write( self.urlopen(url).read() )

def backup(projectname, password, options):
    import sys
    def log(msg):
        if options.quiet: return
        sys.stdout.write(msg)
        sys.stdout.flush()

    try:
        backups = OpenSVNBackups(projectname, options)
        log("logging in... ")
        backups.login(password)
        log("done\n")
        log("backing up Subversion... ")
        backups.backup_svn(1, "HEAD")
        log("done\n")
        log("backing up Trac... ")
        backups.backup_trac()
        log("done\n")

    except LoginFailedError:
        print >>sys.stderr, "login failed, possibly bad projectname or password"
        sys.exit(1)

def interactive():
    "interactive() -> (projectname, password, options)"
    import optparse
    parser = optparse.OptionParser("usage: %prog [options] projectname")

    parser.add_option(
        "-p", "--password",
        help="The project's password (default: prompt the user)")

    parser.add_option(
        "-q", "--quiet", action="store_true", default=False,
        help="Suppress output (default: %default)")

    parser.add_option(
        "-t", "--timestamp", default="%Y-%m-%d-%H_%M_%S",
        help="The suffix to use, in strftime(3) format (default: '%default')")

    parser.add_option(
        "-d", "--dry-run", action="store_true", default=False,
        help="Don't actually do do anything (for testing, default: %default)")

    parser.add_option(
        "-r", "--retries", type="int", default=5,
        help="Number of times to retry the backup (default: %default)")

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error("project name not specified")
    projectname = args[0]

    password = options.password
    if password is None:
        from getpass import getpass
        password = getpass("Enter password for project '%s': " % projectname)
    del options.password

    import time
    options.suffix = time.strftime(options.timestamp)

    return projectname, password, options

if __name__ == "__main__":
    # command-line usage
    projectname, password, options = interactive()

    counter = 0
    while True:
        counter += 1
        if counter > options.retries:
            print >>sys.stderr, "too many failures, exiting"
            sys.exit(1)

        try:
            backup(projectname, password, options)
            raise SystemExit
        except: pass
