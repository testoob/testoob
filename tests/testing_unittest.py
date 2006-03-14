import helpers
helpers.fix_include_path()

import unittest, testoob

import testoob.testing as testing

def _generate_command(output=None, error=None, rc=0):
    """
    Generate an args list that produces the given output, error, and
    return code
    """
    commands = ["import sys"]

    if output is not None:
        assert output.find('"""') < 0
        commands.append(
            'sys.stdout.write("""%s"""); sys.stdout.flush()' % output
        )

    if error is not None:
        assert error.find('"""') < 0
        commands.append('sys.stderr.write("""%s""")' % error)

    commands.append("sys.exit(%d)" % rc)

    return ["python", "-c", "; ".join(commands)]

def _get_results(**kwargs):
    """
    Generate a command with the parameters, run it, and return the
    normalized results
    """
    output, error, rc = testing._run_command(_generate_command(**kwargs))
    return testing._normalize_newlines(output), testing._normalize_newlines(error), rc

class TestingUnitTest(unittest.TestCase):
    def testRunCommandOutput(self):
        self.assertEqual(("abc\n", "", 0), _get_results(output="abc\n"))

    def testRunCommandError(self):
        self.assertEqual(("", "def\n", 0), _get_results(error="def\n"))

    def testCommandLineDefaultIsIgnore(self):
        args = _generate_command(output="aaa", error="bbb", rc=77)
        testing.command_line(args)

def suite(): return unittest.makeSuite(TestingUnitTest)
if __name__ == "__main__": unittest.main()
