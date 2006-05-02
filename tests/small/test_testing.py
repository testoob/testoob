import helpers
helpers.fix_include_path()

import testoob
import testoob.testing as testing
from unittest import TestCase

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

class command_line_tests(TestCase):
    def test_run_command_output(self):
        self.assertEqual(("abc\n", "", 0), _get_results(output="abc\n"))

    def test_run_command_error(self):
        self.assertEqual(("", "def\n", 0), _get_results(error="def\n"))

    def test_command_line_default_is_ignore(self):
        _verify_command_line_success(output="aaa", error="bbb", rc=77)

    def test_command_line_expected_output_success(self):
        _verify_command_line_success(output="a\nb\n", expected_output="a\nb\n")

    def test_command_line_expected_output_failure(self):
        _verify_command_line_failure(output="c\nd\n", expected_output="e\nf\n")

    def test_command_line_expected_error_success(self):
        _verify_command_line_success(error="g\nh\n", expected_error="g\nh\n")

    def test_command_line_expected_error_failure(self):
        _verify_command_line_failure(error="i\nj\n", expected_error="k\nl\n")

    def test_command_line_output_regex_success(self):
        _verify_command_line_success(
                output="abc",
                expected_output_regex="a.c",
            )

    def test_command_line_output_regex_failure(self):
        _verify_command_line_failure(
                output="def",
                expected_output_regex="a.c",
            )

    def test_command_line_rc_success(self):
        _verify_command_line_success(rc=17, expected_rc=17)

    def test_command_line_rc_failure(self):
        _verify_command_line_failure(rc=17, expected_rc=18)

    def test_command_line_error_regex_success(self):
        _verify_command_line_success(
                error="ghijkl",
                expected_error_regex="gh.*l",
            )

    def test_command_line_error_regex_failure(self):
        _verify_command_line_failure(
                error="123456",
                expected_error_regex="2468",
            )

    def test_command_line_rc_predicate_success(self):
        _verify_command_line_success(
                rc = 17,
                rc_predicate = lambda rc: rc != 0
            )

    def test_command_line_rc_predicate_failure(self):
        _verify_command_line_failure(
                rc = 0,
                rc_predicate = lambda rc: rc != 0
            )

if __name__ == "__main__":
    import testoob
    testoob.main()
