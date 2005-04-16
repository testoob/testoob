#!/usr/bin/python
import urllib2, cookielib
from urllib2 import urlopen
from ClientForm import ParseResponse

cookie_jar = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))

def choose_form(action, forms):
    for form in forms:
        if form["action"] == action:
            return form

def login(projectname, password):
    forms = ParseResponse(opener.open("https://opensvn.csie.org"))
    form = choose_form("login", forms)
    form["project"] = projectname
    form["password"] = password

    opener.open(form.click())

def backup_svn(r1, r2):
    "backup subversion repository from r1 to r2."
    filename = "testoob-%s-%s.gz" % (r1, r2)
    url = "https://opensvn.csie.org/getbackup.pl/" + filename
    open(filename, "wb").write( opener.open(url).read() )

PROJECT = "testoob"
PASSWORD = "XXXXXXXX"

print "logging in...",
login(PROJECT, PASSWORD)
print "done."
print "saving subversion repository...",
backup_svn(1, 5)
print "done."
