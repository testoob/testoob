import helpers
helpers.fix_include_path()

import unittest, testoob

_suite_file = helpers.project_subpath("tests/suites.py")

def _create_args(tests=None, options=None):
    import sys
    result = [sys.executable, helpers.executable_path(), _suite_file]
    if options is not None: result += options
    if tests is not None: result += tests
    return result

class CommandLineTestCase(unittest.TestCase):
    def testSuccesfulRunNormal(self):
        args = _create_args(options=[], tests=["CaseDigits"])
        regex = r"""
\.\.\.\.\.\.\.\.\.\.
----------------------------------------------------------------------
Ran 10 tests in \d\.\d+s
OK
""".strip()

        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testSuccesfulRunQuiet(self):
        args = _create_args(options=["-q"], tests=["CaseDigits"])
        regex = r"""
^----------------------------------------------------------------------
Ran 10 tests in \d\.\d+s
OK$
""".strip()

        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testSuccesfulRunVerbose(self):
        args = _create_args(options=["-v"], tests=["CaseDigits"])
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
        args = _create_args(options=["-q"], tests=["CaseFailure"])
        regex = r"""
^======================================================================
FAIL: testFailure \(.*suites\.CaseFailure\.testFailure\)
----------------------------------------------------------------------
.*AssertionError

----------------------------------------------------------------------
Ran 1 test in \d\.\d+s
FAILED \(failures=1\)$
""".strip()

        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testRegex(self):
        args = _create_args(options=["-v", "--regex=A|D|J"], tests=["CaseLetters"])
        regex=r"""
testA \(.*suites\.CaseLetters\.testA\) \.\.\. ok
testD \(.*suites\.CaseLetters\.testD\) \.\.\. ok
testJ \(.*suites\.CaseLetters\.testJ\) \.\.\. ok
""".strip()

        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testVassertSimple(self):
        args = _create_args(options=["--regex=CaseDigits.test0", "--vassert"])
        regex = r"""
test0 \(suites\.CaseDigits\.test0\) \.\.\. ok
  \[ PASSED \(assertEquals\) first: "00" second: "00" \]

----------------------------------------------------------------------
""".strip()
        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testVassertFormatStrings(self):
        args = _create_args(options=["--regex=MoreTests.test.*FormatString",
                                     "--vassert"])
        regex = r"""
test.*FormatString \(suites\.MoreTests\.test.*FormatString\) \.\.\. ok
  \[ PASSED \(assertEquals\) first: "%s" second: "%s" \]

----------------------------------------------------------------------
""".strip()
        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testXMLReporting(self):
        import tempfile
        xmlfile = tempfile.mktemp(".testoob-testXMLReporting")
        args = _create_args(options=["--xml=" + xmlfile], tests=["CaseMixed"])

        try:
            testoob.testing._run_command(args)
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
            import os
            os.unlink(xmlfile)

def suite(): return unittest.makeSuite(CommandLineTestCase)
if __name__ == "__main__": unittest.main()
