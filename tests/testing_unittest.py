import helpers
helpers.fix_include_path()

import unittest, testoob

import testoob.testing as testing

def _generate_command(output=None, error=None, rc=0):
    commands = ["import sys"]
    if output: commands.append('''sys.stdout.write("""%s"""); sys.stdout.flush()''' % output)
    if error: commands.append('''sys.stderr.write("""%s""")''' % error)
    commands.append("sys.exit(%d)" % rc)
    return ["python", "-c", "; ".join(commands)]

def _get_results(**kwargs):
    output, error, rc = testing._run_command(_generate_command(**kwargs))
    return testing._normalize_newlines(output), testing._normalize_newlines(error), rc

class TestingUnitTest(unittest.TestCase):
    def testRunCommandOutput(self):
        self.assertEqual(("abc\n", "", 0), _get_results(output="abc\n"))

    def testRunCommandError(self):
        self.assertEqual(("", "def\n", 0), _get_results(error="def\n"))

    # TODO: add explicit testing for popen2 and subprocess implementations

def suite(): return unittest.makeSuite(TestingUnitTest)
if __name__ == "__main__": unittest.main()
