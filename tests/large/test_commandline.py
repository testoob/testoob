import unittest, testoob, os, sys, tempfile
import helpers
import testoob.testing # for skip()

_suite_file = os.path.abspath(helpers.project_subpath("tests/suites.py"))

def _safe_unlink(filename):
    if os.path.exists(filename):
        os.unlink(filename)

def current_directory():
    from os.path import dirname, abspath, normpath
    return normpath(abspath(dirname(__file__)))

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

def _missing_modules_skip_check(stdout, stderr, rc):
    import re
    match_object = re.search("requires missing modules (\[.*\])", stderr)
    if match_object is not None:
        return "Modules missing: " + match_object.group(1)

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

Failed 1 tests
 - testFailure \(suites\.CaseFailure\)
----------------------------------------------------------------------
Ran 1 test in \d\.\d+s
FAILED \(failures=1\)
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

    def _get_file_report(self, option_name):
        """
        Run Testoob with CaseMixed, creating a file report.

        Cleans up after itself and returns the file's contents.
        """

        def safe_read(filename):
            """
            Read a file while always closing it.

            Works on non-reference-counting platforms such as Jython, where
            open(filename).read() can leak the file object.
            """
            f = open(filename)
            try: return f.read()
            finally: f.close()

        output_file = tempfile.mktemp(".testoob-testing-%s-reporting" % option_name)
        args = _testoob_args(options=["--%s=%s" % (option_name, output_file)], tests=["CaseMixed"])

        try:
            testoob.testing.command_line(
                args,
                skip_check = _missing_modules_skip_check,
                expected_error_regex = 'Ran [0-9]+ tests',
            )

            return safe_read(output_file)

        finally:
            _safe_unlink(output_file)

    def testXMLReporting(self):
        try:
            from elementtree import ElementTree
        except ImportError:
            testoob.testing.skip(reason="Needs ElementTree")

        root = ElementTree.XML( self._get_file_report("xml") )

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

    def testHTMLReporting(self):
        htmlcontents = self._get_file_report("html")

        from testoob.testing import assert_matches
        assert htmlcontents.find("<title>Testoob report</title>") >= 0
        assert htmlcontents.find("def testError(self): raise RuntimeError") >= 0
        assert htmlcontents.find("def testFailure(self): self.fail()") >= 0

        assert_matches(r"testSuccess.*>Success<", htmlcontents)

    def testPDFReporting(self):
        pdfcontents = self._get_file_report("pdf")
        self.assertEquals( '%PDF-1.3', pdfcontents.splitlines()[0] )

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

    def testRepeatsList(self):
        args = _testoob_args(options=["--repeat=3", "--list"], tests=["CaseDigits"])
        expected="""Module: suites (unknown file)
\tClass: CaseDigits (30 test functions)
\t\ttest0() (1st iteration)
\t\ttest0() (2nd iteration)
\t\ttest0() (3ed iteration)
\t\ttest1() (1st iteration)
\t\ttest1() (2nd iteration)
\t\ttest1() (3ed iteration)
\t\ttest2() (1st iteration)
\t\ttest2() (2nd iteration)
\t\ttest2() (3ed iteration)
\t\ttest3() (1st iteration)
\t\ttest3() (2nd iteration)
\t\ttest3() (3ed iteration)
\t\ttest4() (1st iteration)
\t\ttest4() (2nd iteration)
\t\ttest4() (3ed iteration)
\t\ttest5() (1st iteration)
\t\ttest5() (2nd iteration)
\t\ttest5() (3ed iteration)
\t\ttest6() (1st iteration)
\t\ttest6() (2nd iteration)
\t\ttest6() (3ed iteration)
\t\ttest7() (1st iteration)
\t\ttest7() (2nd iteration)
\t\ttest7() (3ed iteration)
\t\ttest8() (1st iteration)
\t\ttest8() (2nd iteration)
\t\ttest8() (3ed iteration)
\t\ttest9() (1st iteration)
\t\ttest9() (2nd iteration)
\t\ttest9() (3ed iteration)
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
            testoob.testing.skip(reason="Unsuported on Windows")
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

Failed 2 tests
 - testBuisy \(suites.CaseSlow\)
 - testSleep \(suites.CaseSlow\)
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

Erred 1 tests
 - testError \(suites\.CaseMixed\)
Failed 1 tests
 - testFailure \(suites\.CaseMixed\)
----------------------------------------------------------------------
Ran 5 tests in (5|6)\.\d+s
FAILED \(failures=1, errors=1\)
"""
        testoob.testing.command_line(args=args, expected_error_regex=regex, expected_rc=1)

    def _check_processes_immediate(self, processes_type):
        # Check that the fail message appears in the middle
        regex = "OK.*FAIL.*OK"
        testoob.testing.command_line(
            args = _testoob_args(
                tests=["FailInTheMiddle"],
                options=["-v", "--immediate", "--processes_%s=2" % processes_type]),
            expected_error_regex = "OK.*FAIL.*OK",
            rc_predicate=lambda rc: rc != 0,
            skip_check = _missing_modules_skip_check,
        )

    def testProcessesOldImmediate(self):
        self._check_processes_immediate("old")

    def testProcessesPyroImmediate(self):
        self._check_processes_immediate("pyro")

    def testSkipWithProcesses(self):
        testoob.testing.command_line(
                _testoob_args(tests=["skipping"], options=["--processes_pyro=2"]),
                expected_error_regex="Skipped 2 tests",
                expected_rc=0,
                skip_check = _missing_modules_skip_check,
        )

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

Erred 1 tests
 - testError \(suites\.CaseVerbous\)
Failed 1 tests
 - testFailure \(suites\.CaseVerbous\)
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
Erred 1 tests
 - testError \(suites\.CaseVerbous\)
Failed 1 tests
 - testFailure \(suites\.CaseVerbous\)
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

    def testSilentCoverage(self):
        helpers.ensure_coverage_support()
        testoob.testing.command_line(
            self._coverageArgs("silent"),
            expected_rc=0,
        )
    def testSlimCoverage(self):
        helpers.ensure_coverage_support()
        testoob.testing.command_line(
            self._coverageArgs("slim"),
            expected_error_regex="covered [0-9]+% of the code",
        )
    def testNormalCoverage(self):
        helpers.ensure_coverage_support()
        testoob.testing.command_line(
            self._coverageArgs("normal"),
            expected_error_regex="covered [0-9]+% of the code",
            expected_output_regex="lines.*cov_n.*module.*path.*TOTAL",
        )
    def testMassiveCoverage(self):
        helpers.ensure_coverage_support()
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
    def testSkippingTests(self):
        testoob.testing.command_line(
                _testoob_args(tests=["skipping"]),
                expected_error_regex='Skipped 2 tests.*Ran 3 tests.*OK',
                expected_rc=0,
        )
    def testSkippingTestsVerbose(self):
        testoob.testing.command_line(
                _testoob_args(options=["-v"], tests=["skipping"]),
                expected_error_regex='SKIPPED.*SKIPPED',
                expected_rc=0,
        )

    def testMultipleSameSuite(self):
        tests = ["CaseDigits", "CaseLetters"]
        stdout, stderr, rc = testoob.testing._run_command(_testoob_args(tests=tests))
        import re
        stderr = re.escape(stderr)
        stderr = re.sub("\d\\\.\d\d\ds", r"\d.\d\d\ds", stderr)
        testoob.testing.command_line(
                _testoob_args(tests=tests*2),
                expected_error_regex=stderr,
                expected_output=stdout,
                expected_rc=rc,
        )

    def testSkipOnInterrupt(self):
        testoob.testing.command_line(
                _testoob_args(tests=["InterruptingTests"]),
                expected_error_regex='Skipped 4 tests.*Test was interrupted.*Ran 4 tests',
                expected_rc=0,
        )

    def testSetUpTearDown(self):
        testoob.testing.command_line(
                _testoob_args(tests=["CaseSetUpTearDown"]),
                expected_error_regex='Ran 1 test.*\nOK',
                expected_rc=0,
        )

    def testSetUpTearDowanRepeat(self):
        testoob.testing.command_line(
                _testoob_args(options=["--repeat=3"], tests=["CaseSetUpTearDown"]),
                expected_error_regex='Ran 3 tests.*\nOK',
                expected_rc=0,
        )

    def testSetUpTearDownTimedRepeat(self):
        testoob.testing.command_line(
                _testoob_args(options=["--timed-repeat=1"], tests=["CaseSetUpTearDown"]),
                expected_error_regex='Ran 1 test.*\nOK',
                expected_rc=0,
        )

    def testCoverageMissingEOL(self):
        helpers.ensure_coverage_support()
        suite_file = os.path.join(current_directory(), "missing_eol_tests.py")
        testoob.testing.command_line(
                _testoob_args(options=["--coverage=slim"], suite_file=suite_file),
                expected_error_regex='Ran 2 tests',
                expected_rc=0,
        )

    def testSilentSuccess(self):
        testoob.testing.command_line(
            _testoob_args(options=["--silent"], tests=["CaseDigits"]),
            expected_error="",
            expected_output="",
            expected_rc=0,
        )

    def testSilentFailure(self):
        testoob.testing.command_line(
            _testoob_args(options=["--silent"], tests=["CaseError"]),
            expected_error  = "",
            expected_output = "",
            rc_predicate    = lambda rc: rc != 0,
        )

    def _check_profiler(self, profiler_name, test_case, rc_predicate):
        stats_filename = tempfile.mktemp(".testoob-testing-profiler-%s.stats" % profiler_name)
        try:
            testoob.testing.command_line(
                _testoob_args(
                    options=["--profiler=" + profiler_name, "--profdata=" + stats_filename],
                    tests=[test_case]),
                rc_predicate=rc_predicate,
                expected_output_regex="[0-9]+ function calls.*in [0-9.]+ CPU seconds",
                skip_check = _missing_modules_skip_check,
            )
        finally:
            _safe_unlink(stats_filename)

    def _check_profiler_success(self, profiler_name):
        self._check_profiler(profiler_name, "CaseDigits", lambda rc: rc == 0)

    def _check_profiler_failure(self, profiler_name):
        self._check_profiler(profiler_name, "CaseMixed", lambda rc: rc != 0)

    def testProfilingHotshotSuccess(self):
        self._check_profiler_success("hotshot")

    def testProfilingHotshotFailure(self):
        self._check_profiler_failure("hotshot")

    def testProfilingProfileSuccess(self):
        self._check_profiler_success("profile")

    def testProfilingProfileFailure(self):
        self._check_profiler_failure("profile")

    def testCommandLineSkipCheckSkipping(self):
        def check(output, error, rc):
            if output.find("glass onion"):
                return "No onion support yet"

        testoob.testing.assert_raises(
            testoob.SkipTestException,

            testoob.testing.command_line, ["echo", "look into a glass onion"],
            skip_check=check,

            expected_regex = 'No onion support yet',
        )

    def testCommandLineSkipCheckNotSkipping(self):
        try:
            testoob.testing.command_line( ["echo", "abc"], skip_check=lambda *args:None )
        except testoob.SkipTestException:
            self.fail("Got unexpected SkipTestException")

    def testTestoobMainExitWithError(self):
        testoob.testing.command_line(
            args = _testoob_args(tests=["CaseError"]),
            rc_predicate = lambda rc: rc != 0,
        )

if __name__ == "__main__":
    testoob.main()
