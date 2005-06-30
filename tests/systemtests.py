import helpers
helpers.fix_include_path()

import unittest, testoob

_suite_file = helpers.project_subpath("tests/suites.py")

class CommandLineTestCase(unittest.TestCase):
    def testSuccesfulRun(self):
        cmd = "python %s %s CaseDigits" % (helpers.executable_path(), _suite_file)
        expected_error_regex = r"""
\.\.\.\.\.\.\.\.\.\.
----------------------------------------------------------------------
Ran 10 tests in 0.0\d+s
OK
""".strip()

        testoob.testing.command_line(
            cmd=cmd, expected_error_regex=expected_error_regex)

def suite(): return unittest.makeSuite(CommandLineTestCase)
if __name__ == "__main__": unittest.main()
