import helpers
helpers.fix_include_path()

import unittest, testoob, os, sys

_suite_file = helpers.project_subpath("tests/suites.py")

def _testoob_args(tests=None, options=None):
    result = [sys.executable, helpers.executable_path(), _suite_file]
    if options is not None: result += options
    if tests is not None: result += tests
    return result

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
test0 \(.*suites\.CaseDigits\.test0\) \.\.\. ok
test1 \(.*suites\.CaseDigits\.test1\) \.\.\. ok
test2 \(.*suites\.CaseDigits\.test2\) \.\.\. ok
test3 \(.*suites\.CaseDigits\.test3\) \.\.\. ok
test4 \(.*suites\.CaseDigits\.test4\) \.\.\. ok
test5 \(.*suites\.CaseDigits\.test5\) \.\.\. ok
test6 \(.*suites\.CaseDigits\.test6\) \.\.\. ok
test7 \(.*suites\.CaseDigits\.test7\) \.\.\. ok
test8 \(.*suites\.CaseDigits\.test8\) \.\.\. ok
test9 \(.*suites\.CaseDigits\.test9\) \.\.\. ok

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
testA \(.*suites\.CaseLetters\.testA\) \.\.\. ok
testD \(.*suites\.CaseLetters\.testD\) \.\.\. ok
testJ \(.*suites\.CaseLetters\.testJ\) \.\.\. ok
""".strip()

        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testVassertSimple(self):
        args = _testoob_args(options=["--regex=CaseDigits.test0", "--vassert"])
        regex = r"""
test0 \(suites\.CaseDigits\.test0\) \.\.\. ok
  \[ PASSED \(assertEquals\) first: "00" second: "00" \]

----------------------------------------------------------------------
""".strip()
        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testVassertFormatStrings(self):
        args = _testoob_args(options=["--regex=MoreTests.test.*FormatString",
                                     "--vassert"])
        regex = r"""
test.*FormatString \(suites\.MoreTests\.test.*FormatString\) \.\.\. ok
  \[ PASSED \(assertEquals\) first: "%s" second: "%s" \]

----------------------------------------------------------------------
""".strip()
        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testImmediateReporting(self):
        args = _testoob_args(tests=["CaseMixed.testFailure", "CaseMixed.testSuccess"],
                            options=["-v", "--immediate"])
        # Check that the fail message appears before testSuccess is run
        regex = "testFailure.*FAIL.*FAIL: testFailure.*Traceback.*testSuccess.*ok"
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
        import tempfile
        xmlfile = tempfile.mktemp(".testoob-testXMLReporting")
        args = _testoob_args(options=["--xml=" + xmlfile], tests=["CaseMixed"])

        try:
            testoob.testing.command_line(args=args, expected_error_regex="FAILED", expected_rc=None)
            from elementtree.ElementTree import parse
            root = parse(xmlfile).getroot()

            # testsuites tag
            self.assertEqual("testsuites", root.tag)

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

            testcase_reports = [extract_info(testcase) for testcase in root.findall("testcase")]

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
            assert htmlcontents.find("<title>TestOOB report</title>") >= 0
            assert htmlcontents.find("def testError(self): raise RuntimeError") >= 0
            assert htmlcontents.find("def testFailure(self): self.fail()") >= 0

            assert_matches(r"testSuccess.*>Success<", htmlcontents)
        finally:
            if os.path.exists(htmlfile):
                os.unlink(htmlfile)

    def testConflictingRegexGlob(self):
        args = _testoob_args(options=["--regex=abc", "--glob=abc"], tests=["CaseLetters"])
        regex=r"The following options can't be specified together: glob, regex"
        testoob.testing.command_line(args=args, expected_error_regex=regex, expected_rc=None)

    def testGlob(self):
        args = _testoob_args(options=["-v", "--glob=*Database*"], tests=["CaseNames"])
        regex=r"""
testDatabaseConnections \(.*suites\.CaseNames\.testDatabaseConnections\) \.\.\. ok
testDatabaseError \(.*suites\.CaseNames\.testDatabaseError\) \.\.\. ok
.*Ran 2 tests
""".strip()
        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testRepeat(self):
        args = _testoob_args(options=["--repeat=7"], tests=["CaseDigits"])
        regex=r"Ran 70 tests"
        testoob.testing.command_line(args=args, expected_error_regex=regex)

def suite(): return unittest.makeSuite(CommandLineTestCase)
if __name__ == "__main__": unittest.main()
