import helpers
import unittest
import testoob.extracting
import suites

class ExtractingTestCase(helpers.TestoobBaseTestCase):
    def _runWithDecorator(self, decorator):
        self._run(suite=suites.suite(), extraction_decorators=[decorator])

    def testRegexExtractorMatchEverything(self):
        self._runWithDecorator(testoob.extracting.regex(".*"))
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

    def testRegexExtractorMatchSome(self):
        self._runWithDecorator(testoob.extracting.regex("(B|C|6)$"))
        self._check_reporter(
                started   = ["testB", "testC", "test6"],
                finished  = ["testB", "testC", "test6"],
                successes = ["testB", "testC", "test6"],
                failures  = [],
                errors    = [],
                asserts   = {
                                "testB": ("assertEquals", None.__class__),
                                "testC": ("assertEquals", None.__class__),
                                "test6": ("assertEquals", None.__class__),
                            },
                stdout    = "",
                stderr    = "",
            )

    def testRegexExtractorMatchNone(self):
        self._runWithDecorator(testoob.extracting.regex("xanadu"))
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

def suite(): return unittest.makeSuite(ExtractingTestCase)

if __name__ == "__main__": unittest.main()
