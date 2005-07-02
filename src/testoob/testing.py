def _run_command(args, input=None):
    """_run_command(args, input=None) -> stdoutstring, stderrstring, returncode
    Runs the command, giving the input if any.
    The command is specified as a list: 'ls -l' would be sent as ['ls', '-l'].
    Returns the standard output and error as strings, and the return code"""
    try:
        from subprocess import Popen, PIPE
    except ImportError:
        # Python 2.2 and 2.3 compatibility
        from compatibility.subprocess import Popen, PIPE

    p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    stdout, stderr = p.communicate(input)
    return stdout, stderr, p.returncode

def assert_equals(expected, actual, msg = None):
    "works like unittest.TestCase.assertEquals"
    if expected == actual: return
    if msg is None:
        msg = '%s != %s' % (expected, actual)
    raise AssertionError(msg)

def assert_matches(regex, actual, msg=None):
    "fail unless regex matches actual (using re.search)"
    import re
    if re.search(regex, actual) is not None: return

    if msg is None:
        msg = "'%(actual)s' doesn't match regular expression '%(regex)s'" % vars()
    raise AssertionError(msg)

def conditionally_assert_equals(expected, actual):
    "assert_equals only if expected is not None"
    if expected is not None:
        assert_equals(expected, actual)

def conditionally_assert_matches(expected_regex, actual):
    "assert_matches only if expected_regex is not None"
    if expected_regex is not None:
        assert_matches(expected_regex, actual)

def command_line(
        args,
        input=None,
        expected_output=None,
        expected_error=None,
        expected_output_regex=None,
        expected_error_regex=None,
        expected_rc=0,):

    # TODO: make errors print full status like working directory, etc.

    # run command
    output, error, rc = _run_command(args, input)

    if expected_output is None and expected_output_regex is None:
        expected_output = ""
    if expected_error is None and expected_error_regex is None:
        expected_error = ""

    # test
    conditionally_assert_equals(expected_error, error)
    conditionally_assert_equals(expected_output, output)
    conditionally_assert_matches(expected_output_regex, output)
    conditionally_assert_matches(expected_error_regex, error)
    conditionally_assert_equals(expected_rc, rc)
