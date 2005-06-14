import helpers
helpers.fix_include_path()

import unittest
import testoob.running
import suites

class TestoobBaseTestCase(unittest.TestCase):
    def setUp(self):
        self.reporter = helpers.ReporterWithMemory()
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
        self._run(suite=suites.suite())
        self._check_reporter(
                started   = suites.all_test_names,
                finished  = suites.all_test_names,
                successes = suites.all_test_names,
                failures  = [],
                errors    = [],
                stdout    = "",
                stderr    = "",
            )

    def testFailureRun(self):
        self._run(suite=suites.CaseFailure.suite())
        self._check_reporter(
                started   = ["testFailure"],
                finished  = ["testFailure"],
                successes = [],
                failures  = ["testFailure"],
                errors    = [],
                stdout    = "",
                stderr    = "",
            )

    def testErrorRun(self):
        self._run(suite=suites.CaseError.suite())
        self._check_reporter(
                started   = ["testError"],
                finished  = ["testError"],
                successes = [],
                failures  = [],
                errors    = ["testError"],
                stdout    = "",
                stderr    = "",
            )

    def testMixedRun(self):
        self._run(suite=suites.CaseMixed.suite())
        self._check_reporter(
                started   = ["testError", "testSuccess", "testFailure"],
                finished  = ["testError", "testSuccess", "testFailure"],
                successes = ["testSuccess"],
                failures  = ["testFailure"],
                errors    = ["testError"],
                stdout    = "",
                stderr    = "",
            )

def suite(): return unittest.makeSuite(RunningTestCase)
if __name__ == "__main__": unittest.main()
