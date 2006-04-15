import unittest, urllib

class NewsSitesTestCase(unittest.TestCase):
    def testSlashdot(self):
        urllib.urlopen("http://www.slashdot.org").read()
    def testWired(self):
        urllib.urlopen("http://www.wired.com").read()
    def testTheOnion(self):
        urllib.urlopen("http://www.theonion.com").read()

class OtherSitesTestCase(unittest.TestCase):
    def testYahoo(self):
        urllib.urlopen("http://www.yahoo.com").read()
    def testGoogle(self):
        urllib.urlopen("http://www.google.com").read()
    def testPython(self):
        urllib.urlopen("http://www.python.org").read()
    def testThinlet(self):
        urllib.urlopen("http://thinlet.sourceforge.net").read()

def suite():
    result = unittest.TestSuite()
    result.addTest( unittest.makeSuite(NewsSitesTestCase) )
    result.addTest( unittest.makeSuite(OtherSitesTestCase) )
    return result
