import helpers
helpers.fix_include_path()

import unittest, testoob

import testoob.testing as testing

def _generate_command(output="", error="", rc=0):
    """
    Generate an args list that produces the given output, error, and
    return code
    """
    assert output.find('"""') < 0
    assert error.find('"""') < 0
    python_commands = (
        'import sys',
        'sys.stdout.write("""%s""")' % output,
        'sys.stdout.flush()',
        'sys.stderr.write("""%s""")' % error,
        'sys.stderr.flush()',
        'sys.exit(%d)' % rc,
    )

    import sys
    return [sys.executable, "-c", "; ".join(python_commands)]

def _get_results(**kwargs):
    """
    Generate a command with the parameters, run it, and return the
    normalized results
    """
    output, error, rc = testing._run_command(_generate_command(**kwargs))
    return testing._normalize_newlines(output), testing._normalize_newlines(error), rc

def _verify_command_line_success(output="", error="", rc=0, **kwargs):
    "Convenience function"
    args = _generate_command(output=output, error=error, rc=rc)
    testing.command_line(args, **kwargs)

def _verify_command_line_failure(output="", error="", rc=0, **kwargs):
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

    def testCommandLineExpectedErrorSuccess(self):
        _verify_command_line_success(error="g\nh\n", expected_error="g\nh\n")

    def testCommandLineExpectedErrorFailure(self):
        _verify_command_line_failure(error="i\nj\n", expected_error="k\nl\n")

    def testCommandLineOutputRegexSuccess(self):
        _verify_command_line_success(
                output="abc",
                expected_output_regex="a.c",
            )

    def testCommandLineOutputRegexFailure(self):
        _verify_command_line_failure(
                output="def",
                expected_output_regex="a.c",
            )

    def testCommandLineRcSuccess(self):
        _verify_command_line_success(rc=17, expected_rc=17)

    def testCommandLineRcFailure(self):
        _verify_command_line_failure(rc=17, expected_rc=18)

    def testCommandLineErrorRegexSuccess(self):
        _verify_command_line_success(
                error="ghijkl",
                expected_error_regex="gh.*l",
            )

    def testCommandLineErrorRegexFailure(self):
        _verify_command_line_failure(
                error="123456",
                expected_error_regex="2468",
            )

    def testCommandLineRcPredicateSuccess(self):
        _verify_command_line_success(
                rc = 17,
                rc_predicate = lambda rc: rc != 0
            )

    def testCommandLineRcPredicateFailure(self):
        _verify_command_line_failure(
                rc = 0,
                rc_predicate = lambda rc: rc != 0
            )

if __name__ == "__main__":
    import testoob
    testoob.main()
