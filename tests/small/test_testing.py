import helpers
helpers.fix_include_path()

import testoob
import testoob.testing as tt
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
    output, error, rc = tt._run_command(_generate_command(**kwargs))
    return tt._normalize_newlines(output), tt._normalize_newlines(error), rc

def _verify_command_line_success(output="", error="", rc=0, **kwargs):
    "Convenience function"
    args = _generate_command(output=output, error=error, rc=rc)
    tt.command_line(args, **kwargs)

def _verify_command_line_failure(output="", error="", rc=0, **kwargs):
    args = _generate_command(output=output, error=error, rc=rc)
    tt.assert_raises(
        AssertionError,
        tt.command_line,
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

class assert_raises_tests(TestCase):
    # Yes, we'll be testing assert_raises with TestCase.assertRaises. Isn't
    # that a hoot?
    def test_expected_exception(self):
        def func(): raise ValueError()
        tt.assert_raises(ValueError, func)

    def test_missing_exception(self):
        def func(): pass
        self.assertRaises(
            AssertionError, tt.assert_raises, Exception, func)

    def test_args_expected_exception(self):
        def func(x):
            if x < 10: raise TypeError()
        tt.assert_raises(TypeError, func, 5)

    def test_args_missing_exception(self):
        def func(x):
            if x < 10: raise TypeError()
        self.assertRaises(
            AssertionError, tt.assert_raises, TypeError, func, 10)

    def test_kwargs_expected_exception(self):
        def func(**kwargs):
            if kwargs["x"] < 10: raise EnvironmentError()
        tt.assert_raises(EnvironmentError, func, x=5)

    def test_kwargs_missing_exception(self):
        def func(**kwargs):
            if kwargs["x"] < 10: raise EnvironmentError()
        self.assertRaises(
            AssertionError, tt.assert_raises, EnvironmentError, func, x=10)

    def test_expected_args_success(self):
        def func(): raise RuntimeError(123, 456)
        tt.assert_raises(RuntimeError, func, expected_args=(123,456))

    def test_expected_args_failure(self):
        def func(): raise RuntimeError(123, 456)
        self.assertRaises(
            AssertionError, tt.assert_raises, RuntimeError, func,
            expected_args=("abc", "def")
        )

    def test_expected_args_failure_error_message(self):
        def func(): raise RuntimeError(123, 456)
        try:
            tt.assert_raises(RuntimeError, func, expected_args=("abc", "def"))
        except AssertionError, e:
            import re
            expected = re.escape("func() raised exceptions.RuntimeError with unexpected args: expected=('abc', 'def'), actual=(123, 456)")
            tt.assert_matches( expected, str(e) )

if __name__ == "__main__":
    import testoob
    testoob.main()
