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

def _verify_command_line_success(output=None, error=None, rc=0, **kwargs):
    "Convenience function"
    args = _generate_command(output=output, error=error, rc=rc)
    testing.command_line(args, **kwargs)

def _verify_command_line_failure(output=None, error=None, rc=0, **kwargs):
    args = _generate_command(output=output, error=error, rc=rc)
    testing.assert_raises(
        AssertionError,
        testing.command_line,
        args, 
        **kwargs
    )
    
class TestingUnitTest(unittest.TestCase):
    def testRunCommandOutput(self):
        self.assertEqual(("abc\n", "", 0), _get_results(output="abc\n"))

    def testRunCommandError(self):
        self.assertEqual(("", "def\n", 0), _get_results(error="def\n"))

    def testCommandLineDefaultIsIgnore(self):
        _verify_command_line_success(output="aaa", error="bbb", rc=77)

    def testCommandLineExpectedOutputSuccess(self):
        _verify_command_line_success(output="a\nb\n", expected_output="a\nb\n")

    def testCommandLineExpectedOutputFailure(self):
        _verify_command_line_failure(output="c\nd\n", expected_output="e\nf\n")

def suite(): return unittest.makeSuite(TestingUnitTest)
if __name__ == "__main__": unittest.main()
