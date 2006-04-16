import helpers
helpers.fix_include_path()

import unittest, testoob, os, sys

_suite_file = helpers.project_subpath("tests/suites.py")

def _testoob_args(tests=None, options=None, suite_file = _suite_file):
    result = [sys.executable, helpers.executable_path(), suite_file]
    if options is not None: result += options
    if tests is not None: result += tests
    return result

def _grep(pattern, string):
    import re
    compiled = re.compile(pattern)
    return "\n".join([
            line
            for line in string.splitlines()
            if compiled.search(line)
        ])

def _run_testoob(args, grep=None):
    stdout, stderr, rc = testoob.testing._run_command(args)
    if grep is not None:
        return _grep(grep, stderr)
    return stderr

class CommandLineTestCase(unittest.TestCase):
    def testSuccesfulRunNormal(self):
        args = _testoob_args(options=[], tests=["CaseDigits"])
        regex = r"""
\.\.\.\.\.\.\.\.\.\.
----------------------------------------------------------------------
Ran 10 tests in \d\.\d+s
OK
""".strip()

        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testSuccesfulRunQuiet(self):
        args = _testoob_args(options=["-q"], tests=["CaseDigits"])
        regex = r"""
^----------------------------------------------------------------------
Ran 10 tests in \d\.\d+s
OK$
""".strip()

        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testSuccesfulRunVerbose(self):
        args = _testoob_args(options=["-v"], tests=["CaseDigits"])
        regex = r"""
test0 \(.*suites\.CaseDigits\.test0\) \.\.\. OK
test1 \(.*suites\.CaseDigits\.test1\) \.\.\. OK
test2 \(.*suites\.CaseDigits\.test2\) \.\.\. OK
test3 \(.*suites\.CaseDigits\.test3\) \.\.\. OK
test4 \(.*suites\.CaseDigits\.test4\) \.\.\. OK
test5 \(.*suites\.CaseDigits\.test5\) \.\.\. OK
test6 \(.*suites\.CaseDigits\.test6\) \.\.\. OK
test7 \(.*suites\.CaseDigits\.test7\) \.\.\. OK
test8 \(.*suites\.CaseDigits\.test8\) \.\.\. OK
test9 \(.*suites\.CaseDigits\.test9\) \.\.\. OK

----------------------------------------------------------------------
Ran 10 tests in \d\.\d+s
OK
""".strip()

        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testFailureRunQuiet(self):
        args = _testoob_args(options=["-q"], tests=["CaseFailure"])
        regex = r"""
^======================================================================
FAIL: testFailure \(.*suites\.CaseFailure\.testFailure\)
----------------------------------------------------------------------
.*AssertionError

----------------------------------------------------------------------
Ran 1 test in \d\.\d+s
FAILED \(failures=1\)$
""".strip()

        testoob.testing.command_line(args=args, expected_error_regex=regex, expected_rc=1)

    def testRegex(self):
        args = _testoob_args(options=["-v", "--regex=A|D|J"], tests=["CaseLetters"])
        regex=r"""
testA \(.*suites\.CaseLetters\.testA\) \.\.\. OK
testD \(.*suites\.CaseLetters\.testD\) \.\.\. OK
testJ \(.*suites\.CaseLetters\.testJ\) \.\.\. OK
""".strip()

        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testVassertSimple(self):
        args = _testoob_args(options=["--regex=CaseDigits.test0", "--vassert"])
        regex = r"""
test0 \(suites\.CaseDigits\.test0\) \.\.\. OK
  \[ PASSED \(assertEquals\) first: "00" second: "00" \]

----------------------------------------------------------------------
""".strip()
        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testVassertFormatStrings(self):
        args = _testoob_args(options=["--regex=MoreTests.test.*FormatString",
                                     "--vassert"])
        regex = r"""
test.*FormatString \(suites\.MoreTests\.test.*FormatString\) \.\.\. OK
  \[ PASSED \(assertEquals\) first: "%s" second: "%s" \]

----------------------------------------------------------------------
""".strip()
        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testImmediateReporting(self):
        args = _testoob_args(tests=["CaseMixed.testFailure", "CaseMixed.testSuccess"],
                            options=["-v", "--immediate"])
        # Check that the fail message appears before testSuccess is run
        regex = "testFailure.*FAIL.*FAIL: testFailure.*Traceback.*testSuccess.*OK"
        testoob.testing.command_line(args=args, expected_error_regex=regex, expected_rc=1)

    def testLaunchingPdb(self):
        args = _testoob_args(tests=["CaseMixed.testFailure"], options=["--debug"])
        output_regex="Debugging for failure in test: testFailure \(suites\.CaseMixed\.testFailure\).*raise self\.failureException, msg.*\(Pdb\)"
        error_regex="" # accept anything on the standard error
        testoob.testing.command_line(args=args,
                                     expected_output_regex=output_regex,
                                     expected_error_regex=error_regex,
                                     expected_rc=1)

    def testXMLReporting(self):
        try:
            from elementtree.ElementTree import parse
        except ImportError:
            return # TODO: raise Skip
        import tempfile
        xmlfile = tempfile.mktemp(".testoob-testXMLReporting")
        args = _testoob_args(options=["--xml=" + xmlfile], tests=["CaseMixed"])

        try:
            testoob.testing.command_line(args=args, expected_error_regex="FAILED", expected_rc=None)
            root = parse(xmlfile).getroot()

            # testsuites tag
            self.assertEqual("results", root.tag)

            # ensures only one testsuites element
            [testsuites] = root.findall("testsuites")
            

            def extract_info(testcase):
                class Struct: pass
                result = Struct()
                result.tag = testcase.tag
                result.name = testcase.attrib["name"]
                result.result = testcase.find("result").text
                failure = testcase.find("failure")
                result.failure = failure is not None and failure.attrib["type"] or None
                error = testcase.find("error")
                result.error = error is not None and error.attrib["type"] or None
                return result

            testcase_reports = [extract_info(testcase) for testcase in testsuites.findall("testcase")]

            # ensure one testcase of each type
            [success] = [x for x in testcase_reports if x.result == "success"]
            [failure] = [x for x in testcase_reports if x.result == "failure"]
            [error]   = [x for x in testcase_reports if x.result == "error"]

            def check_result(testcase, name=None, failure=None, error=None):
                self.assertEqual("testcase", testcase.tag)
                self.assertEqual(name, testcase.name)
                self.assertEqual(failure, testcase.failure)
                self.assertEqual(error, testcase.error)

            check_result(success, name="testSuccess (suites.CaseMixed)")
            check_result(failure, name="testFailure (suites.CaseMixed)",
                                  failure="exceptions.AssertionError")
            check_result(error,   name="testError (suites.CaseMixed)",
                                  error="exceptions.RuntimeError")

        finally:
            if os.path.exists(xmlfile):
                os.unlink(xmlfile)

    def testHTMLReporting(self):
        try:
            import tempfile
            htmlfile = tempfile.mktemp(".testoob-testHTMLReporting")
            args = _testoob_args(options=["--html=" + htmlfile], tests=["CaseMixed"])

            stdout, stderr, rc = testoob.testing._run_command(args)
            if stderr.find("option '--html' requires missing modules") >= 0:
                # HTML reporting isn't expected to work
                return

            htmlcontents = open(htmlfile).read()

            from testoob.testing import assert_matches
            assert htmlcontents.find("<title>Testoob report</title>") >= 0
            assert htmlcontents.find("def testError(self): raise RuntimeError") >= 0
            assert htmlcontents.find("def testFailure(self): self.fail()") >= 0

            assert_matches(r"testSuccess.*>Success<", htmlcontents)
        finally:
            if os.path.exists(htmlfile):
                os.unlink(htmlfile)

    def testGlob(self):
        args = _testoob_args(options=["-v", "--glob=*Database*"], tests=["CaseNames"])
        regex=r"""
testDatabaseConnections \(.*suites\.CaseNames\.testDatabaseConnections\) \.\.\. OK
testDatabaseError \(.*suites\.CaseNames\.testDatabaseError\) \.\.\. OK
.*Ran 2 tests
""".strip()
        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testRepeat(self):
        args = _testoob_args(options=["--repeat=7"], tests=["CaseDigits"])
        regex=r"Ran 70 tests"
        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testRepeatIterationPrint(self):
        args = _testoob_args(options=["--repeat=10", "-v"], tests=["MoreTests"])
        regex = r""".*\(1st iteration\).*
.*\(2nd iteration\).* OK
.*\(3ed iteration\).* OK
.*\(4th iteration\).* OK
.*\(5th iteration\).* OK
.*\(6th iteration\).* OK
.*\(7th iteration\).* OK
.*\(8th iteration\).* OK
.*\(9th iteration\).* OK
.*\(10th iteration\).* OK

----------------------------------------------------------------------
"""
        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testList(self):
        args = _testoob_args(options=["--list"], tests=["CaseDigits"])
        expected="""Module: suites (unknown file)
\tClass: CaseDigits (10 test functions)
\t\ttest0()
\t\ttest1()
\t\ttest2()
\t\ttest3()
\t\ttest4()
\t\ttest5()
\t\ttest6()
\t\ttest7()
\t\ttest8()
\t\ttest9()
"""
        testoob.testing.command_line(args=args, expected_output=expected)

    def testListDocstrings(self):
        args = _testoob_args(options=["--list"], tests=["CaseDocstring"])
        expected="""Module: suites (unknown file)
\tClass: CaseDocstring (1 test functions)
\t\ttestPass() - this test always passes
"""
        testoob.testing.command_line(args=args, expected_output=expected)

    def testStopOnFail(self):
        args = _testoob_args(options=["--stop-on-fail"], tests=["CaseMixed"])
        regex=r"""E
======================================================================
ERROR: testError \(suites\.CaseMixed\.testError\)
----------------------------------------------------------------------
"""
        testoob.testing.command_line(args=args, expected_error_regex=regex, expected_rc=1)

    def testTimeOut(self):
        if sys.platform.startswith("win"):
            return # XXX disabled on windows, no SIGALRM
        args = _testoob_args(options=["--timeout=1"], tests=["CaseSlow"])
        regex=r"""FF
======================================================================
FAIL: testBuisy \(suites\.CaseSlow\.testBuisy\)
----------------------------------------------------------------------
.*
AssertionError: Timeout

======================================================================
FAIL: testSleep \(suites\.CaseSlow\.testSleep\)
----------------------------------------------------------------------
.*
AssertionError: Timeout

----------------------------------------------------------------------
Ran 2 tests in 2\.\d+s
"""
        testoob.testing.command_line(args=args, expected_error_regex=regex, expected_rc=1)

    def testTimedRepeat(self):
        args = _testoob_args(options=["--timed-repeat=1"], tests=["CaseMixed", "CaseSlow"])
        regex=r"""EF\.\.\.
======================================================================
ERROR: testError \(suites\.CaseMixed\.testError\)
----------------------------------------------------------------------
.*
RuntimeError

======================================================================
FAIL: testFailure \(suites\.CaseMixed\.testFailure\)
----------------------------------------------------------------------
.*
AssertionError

----------------------------------------------------------------------
Ran 5 tests in (5|6)\.\d+s
FAILED \(failures=1, errors=1\)
"""
        testoob.testing.command_line(args=args, expected_error_regex=regex, expected_rc=1)

    def testProcessesImmediate(self):
        return # XXX TODO remove this
        args = _testoob_args(tests=["CaseMixed.testFailure", "CaseMixed.testSuccess"],
                            options=["-v", "--immediate", "--processes=2"])
        # Check that the fail message appears before testSuccess is run
        regex = "testFailure.*FAIL.*FAIL: testFailure.*Traceback.*testSuccess.*OK"
        testoob.testing.command_line(args=args, expected_error_regex=regex, expected_rc=1)

    def testCaptureOutput(self):
        args = _testoob_args(options=["--capture"], tests=["CaseVerbous"])
        regex=r"""EF\.
======================================================================
ERROR: testError \(suites\.CaseVerbous\.testError\)
----------------------------------------------------------------------
.*
RuntimeError
======================================================================
Run's output
----------------------------------------------------------------------
Starting test
Erroring\.\.\.

======================================================================
FAIL: testFailure \(suites\.CaseVerbous\.testFailure\)
----------------------------------------------------------------------
.*
AssertionError
======================================================================
Run's output
----------------------------------------------------------------------
Starting test
Failing\.\.\.

----------------------------------------------------------------------
Ran 3 tests in 0\.\d+s
FAILED \(failures=1, errors=1\)
"""
        testoob.testing.command_line(args=args, expected_error_regex=regex, expected_rc=1)

    def testCaptureImmediate(self):
        args = _testoob_args(options=["--capture", "--immediate"], tests=["CaseVerbous"])
        regex=r"""E
======================================================================
ERROR: testError \(suites\.CaseVerbous\.testError\)
----------------------------------------------------------------------
.*
RuntimeError
======================================================================
Run's output
----------------------------------------------------------------------
Starting test
Erroring\.\.\.
======================================================================
F
======================================================================
FAIL: testFailure \(suites\.CaseVerbous\.testFailure\)
----------------------------------------------------------------------
.*
AssertionError
======================================================================
Run's output
----------------------------------------------------------------------
Starting test
Failing\.\.\.
======================================================================
\.
----------------------------------------------------------------------
Ran 3 tests in 0\.\d+s
FAILED \(failures=1, errors=1\)
"""
        testoob.testing.command_line(args=args, expected_error_regex=regex, expected_rc=1)

    def testRandomizeOrderSanity(self):
        args = _testoob_args(options=["--randomize-order"], tests=["CaseDigits"])
        regex = "Ran 10 tests in \d\.\d+s\nOK"
        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testRandomizeOrder(self):
        # Given a perfect RNG, this has a chance of 2^(-88) of failing randomly
        # (on 26 tests), which is probably smaller than the chance I'll find a
        # million dollars in my socks.
        args = _testoob_args(options=["-v", "--randomize-order"],
                             tests=["CaseLetters"])

        stderr1 = _run_testoob(args, grep="^test.*OK$")
        stderr2 = _run_testoob(args, grep="^test.*OK$")

        self.assertNotEqual(stderr1, stderr2)

    def testRandomizeSeed(self):
        # Same chances of random failure as testRandomizeOrder
        args = _testoob_args(options=["-v", "--randomize-order"],
                             tests=["CaseLetters"])
        stderr_order = _run_testoob(args)

        # extract seed from the output
        seed = int(_grep('^seed=', stderr_order).split("=")[1])

        # keep just the tests
        stderr_order = _grep("^test.*OK$", stderr_order)

        args_seed = _testoob_args(options=["-v", "--randomize-seed=%d"%seed],
                                  tests=["CaseLetters"])
        stderr_seed = _run_testoob(args_seed, grep="^test.*OK$")

        self.assertEqual(stderr_order, stderr_seed)

    def _coverageArgs(self, coverage_amount):
        current_directory = os.path.dirname(__file__)
        return _testoob_args(
            options=["--coverage=%s" % coverage_amount],
            suite_file=os.path.join(current_directory, "dummyprojecttests.py"),
        )

    def _coverage_supported(self):
        # Coverage requires 'trace' module, Python 2.3 and higher
        return sys.version_info >= (2, 3)

    def testSilentCoverage(self):
        if not self._coverage_supported(): return # SKIP
        testoob.testing.command_line(
            self._coverageArgs("silent"),
            expected_rc=0,
        )
    def testSlimCoverage(self):
        if not self._coverage_supported(): return # SKIP
        testoob.testing.command_line(
            self._coverageArgs("slim"),
            expected_error_regex="covered [0-9]+% of the code",
        )
    def testNormalCoverage(self):
        if not self._coverage_supported(): return # SKIP
        testoob.testing.command_line(
            self._coverageArgs("normal"),
            expected_error_regex="covered [0-9]+% of the code",
            expected_output_regex="lines.*cov_n.*module.*path.*TOTAL",
        )
    def testMassiveCoverage(self):
        if not self._coverage_supported(): return # SKIP
        testoob.testing.command_line(
            self._coverageArgs("massive"),
            expected_error_regex="covered [0-9]+% of the code",
            expected_output_regex="missing.*\['[0-9]+'",
        )
    def testTestMethodRegex(self):
        testoob.testing.command_line(
                _testoob_args(options=["--test-method-regex=Test$"],
                              tests=["CaseDifferentTestNameSignatures"]),
                expected_error_regex="Ran 1 test.*OK",
                expected_rc=0,
        )
    def testTestMethodGlob(self):
        testoob.testing.command_line(
                _testoob_args(options=["--test-method-glob=check*"],
                              tests=["CaseDifferentTestNameSignatures"]),
                expected_error_regex="Ran 1 test.*OK",
                expected_rc=0,
        )
    def testNonexistantTestCase(self):
        testoob.testing.command_line(
                _testoob_args(tests=["NoSuchTest"]),
                expected_error_regex="Can't find test case 'NoSuchTest'",
                expected_rc=1,
        )
    def testThreadsSanity(self):
        testoob.testing.command_line(
                _testoob_args(options=["--threads=3"], tests=["CaseDigits"]),
                expected_error_regex='Ran 10 tests.*OK',
                expected_rc=0,
        )

if __name__ == "__main__":
    testoob.main()
