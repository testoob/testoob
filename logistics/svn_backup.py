#!/usr/bin/python

class LoginFailedError(RuntimeError): pass

class OpenSVNBackups:
    def __init__(self, projectname):
        self.projectname = projectname
        self._opener = None

    def opener(self):
        if self._opener is None:
            self._opener = self.new_opener()
        return self._opener

    def open(self, url):
        return self.opener().open(url)

    def new_opener(self):
        from cookielib import CookieJar
        from urllib2 import build_opener, HTTPCookieProcessor
        return build_opener(HTTPCookieProcessor(CookieJar()))

    def choose_form(self, action, forms):
        for form in forms:
            if form["action"] == action:
                return form
        
    def login(self, password):
        from ClientForm import ParseResponse
        forms = ParseResponse(self.open("https://opensvn.csie.org"))
        form = self.choose_form("login", forms)
        form["project"] = self.projectname
        form["password"] = password

        result = self.open(form.click()).read()
        if result == 'login failed':
            raise LoginFailedError()

    def save_url(self, url, filename):
        open(filename, "wb").write( self.open(url).read() )

    def backup_svn(self, r1, r2):
        "backup subversion repository from r1 to r2."
        filename = "%s-%s-%s.gz" % (self.projectname, r1, r2)
        url = "https://opensvn.csie.org/getbackup.pl/" + filename
        self.save_url(url, filename)

    def backup_trac(self):
        filename = "%s-trac.tgz" % self.projectname
        url = "https://opensvn.csie.org/getbackup.pl/%s?action=trac" % filename
        self.save_url(url, filename)

def backup(projectname, password):
    backups = OpenSVNBackups(projectname)
    backups.login(password)
    backups.backup_svn(1, 6)
    backups.backup_trac()
