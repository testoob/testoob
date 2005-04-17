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

    def __init__(self, projectname):
        "__init__(projectname) -> initialize a backups object for the project"
        self.projectname = projectname
        self.opener = self.new_opener()

    def login(self, password):
        "login(password) -> log into OpenSVN"
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
        filename = "%s-%s-%s.gz" % (self.projectname, r1, r2)
        url = "https://opensvn.csie.org/getbackup.pl/" + filename
        self.save_url(url, filename)

    def backup_trac(self):
        "backup_trac() -> backup trac repository"
        filename = "%s-trac.tgz" % self.projectname
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
        open(filename, "wb").write( self.urlopen(url).read() )

def backup(projectname, password, max_svn_revision):
    backups = OpenSVNBackups(projectname)
    backups.login(password)
    backups.backup_svn(1, max_svn_revision)
    backups.backup_trac()
