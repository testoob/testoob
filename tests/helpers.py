def project_subpath(*components):
    from os.path import dirname, join, normpath
    return normpath(join(dirname(__file__), "..", *components))

def module_path():
    return project_subpath("src")

def executable_path():
    return project_subpath("src", "testoob", "testoob")

def fix_include_path():
    import sys
    if module_path() not in sys.path:
        sys.path.insert(0, module_path())

fix_include_path()

class ReporterWithMemory:
    "A reporter that remembers info on the test fixtures run"
    def __init__(self):
        self.started = []
        self.successes = []
        self.errors = []
        self.failures = []
        self.finished = []
        self.asserts = {}
        self.stdout = ""
        self.stderr = ""

        self.has_started = False
        self.is_done = False

    def _append_test(self, l, test):
        l.append(str(test).split()[0])

    def start(self):
        self.has_started = True
    def done(self):
        self.is_done = True
    def startTest(self, test):
        self._append_test(self.started, test)
    def stopTest(self, test):
        self._append_test(self.finished, test)
    def addError(self, test, err):
        self._append_test(self.errors, test)
    def addFailure(self, test, err):
        self._append_test(self.failures, test)
    def addSuccess(self, test):
        self._append_test(self.successes, test)
    def addAssert(self, test, assertName, varList, err):
        self.asserts[str(test).split()[0]] = (assertName, err.__class__)

    def __str__(self):
        attrs = ("started","successes","errors","failures","finished","stdout","stderr")
        return "\n".join(["%s = %s" % (attr, getattr(self,attr)) for attr in attrs])

import unittest
import testoob.running
class TestoobBaseTestCase(unittest.TestCase):
    def setUp(self):
        self.reporter = ReporterWithMemory()
    def tearDown(self):
        del self.reporter
    def _check_reporter(self, **kwargs):
        for attr, expected in kwargs.items():
            actual = getattr(self.reporter, attr)
            if type(expected) == type([]):
                expected.sort()
                actual.sort()
            self.assertEqual(expected, actual)

    def _run(self, **kwargs):
        testoob.running.run(reporters=[self.reporter], **kwargs)

