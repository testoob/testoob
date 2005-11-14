import unittest
import helpers, suites

class RunningTestCase(helpers.TestoobBaseTestCase):
    def testSuccessfulRun(self):
        self._run(suite=suites.suite())
        self._check_reporter(
                started   = suites.all_test_names,
                finished  = suites.all_test_names,
                successes = suites.all_test_names,
                failures  = [],
                errors    = [],
                asserts   = suites.all_asserts,
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
                asserts   = {"testFailure": ("fail", AssertionError)},
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
                asserts   = {},
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
                asserts   = {"testFailure": ("fail", AssertionError)},
                stdout    = "",
                stderr    = "",
            )

    def testEmptyRun(self):
        self._run(suite=suites.CaseEmpty.suite())
        self._check_reporter(
                started   = [],
                finished  = [],
                successes = [],
                failures  = [],
                errors    = [],
                asserts   = {},
                stdout    = "",
                stderr    = "",
            )

    def testAssertRaises(self):
        self._run(suite=suites.AssertRaisesTests.suite())
        self._check_reporter(
                started   = ["testAssertRaisesArgs", "testAssertRaisesArgsKwargs", "testAssertRaisesKwargs"],
                finished  = ["testAssertRaisesArgs", "testAssertRaisesArgsKwargs", "testAssertRaisesKwargs"],
                successes = ["testAssertRaisesArgs", "testAssertRaisesArgsKwargs", "testAssertRaisesKwargs"],
                failures  = [],
                errors    = [],
                asserts   = {"testAssertRaisesArgs": ("assertRaises", None.__class__),
                             "testAssertRaisesArgsKwargs": ("assertRaises", None.__class__),
                             "testAssertRaisesKwargs": ("assertRaises", None.__class__),
                            },
                stdout    = "",
                stderr    = "",
            )

def suite(): return unittest.makeSuite(RunningTestCase)
if __name__ == "__main__": unittest.main()
