import helpers
helpers.fix_include_path()

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
            actual = getattr(self.reporter, attr)
            if type(expected) == type([]):
                expected.sort()
                actual.sort()
            self.assertEqual(expected, actual)

    def _run(self, **kwargs):
        testoob.running.run(reporters=[self.reporter], **kwargs)

class RunningTestCase(TestoobBaseTestCase):
    def testSuccessfulRun(self):
        self._run(suite=regular_suite.suite())
        self._check_reporter(
                started   = regular_suite.all_test_names,
                finished  = regular_suite.all_test_names,
                successes = regular_suite.all_test_names,
                failures  = [],
                errors    = [],
                stdout    = "",
                stderr    = "",
            )

    def testMixedRun(self):
        self._run(suite=regular_suite.CaseMixed.suite())
        self._check_reporter(
                started   = ["testError", "testSuccess", "testFailure"],
                finished  = ["testError", "testSuccess", "testFailure"],
                successes = ["testSuccess"],
                failures  = ["testFailure"],
                errors    = ["testError"],
                stdout    = "",
                stderr    = "",
            )


if __name__ == "__main__": unittest.main()
