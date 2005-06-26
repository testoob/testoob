import helpers
helpers.fix_include_path()

import unittest, testoob

class CommandLineTestCase(unittest.TestCase):
    def testSuccesfulRun(self):
        cmd = "python ../src/testoob/testoob suites.py Casedigits"
        expected_output_regex = r"""
\.\.\.\.\.\.\.\.\.\.
----------------------------------------------------------------------
Ran 10 tests in 0.0\d+s
OK
""".strip()

        testoob.testing.command_line(
            cmd=cmd, expected_output_regex=expected_output_regex)

def suite(): return unittest.makeSuite(CommandLineTestCase)
if __name__ == "__main__": unittest.main()
