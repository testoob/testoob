def fix_include_path():
    from os.path import dirname, join, normpath
    module_path = normpath(join(dirname(__file__), "..", "src"))
    import sys
    sys.path.insert(0, module_path)
fix_include_path()

class ReporterWithMemory:
    "A reporter that remembers info on the test fixtures run"
    def __init__(self):
        self.started = []
        self.successes = []
        self.errors = []
        self.failures = []
        self.finished = []
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

    def __str__(self):
        attrs = ("started","successes","errors","failures","finished","stdout","stderr")
        return "\n".join(["%s = %s" % (attr, getattr(self,attr)) for attr in attrs])

import unittest
import testoob.running
import regular_suite

class TestoobBaseTestCase(unittest.TestCase):
    def setUp(self):
        self.reporter = ReporterWithMemory()
    def tearDown(self):
        del self.reporter
    def _check_reporter(self, **kwargs):
        for attr, expected in kwargs.items():
            self.assertEqual(expected, getattr(self.reporter, attr))

class RunningTestCase(TestoobBaseTestCase):
    def testRun(self):
        testoob.running.run(suite=regular_suite.suite(),
                            reporters=[self.reporter])
        self._check_reporter(
                started   = regular_suite.all_test_names,
                finished  = regular_suite.all_test_names,
                successes = regular_suite.all_test_names,
                failures  = [],
                errors    = [],
                stdout    = "",
                stderr    = "",
            )

if __name__ == "__main__": unittest.main()
