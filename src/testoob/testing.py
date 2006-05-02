# Testoob, Python Testing Out Of (The) Box
# Copyright (C) 2005-2006 The Testoob Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"Useful testing fuctions."

__unittest=1

class TestoobAssertionError(AssertionError):
    def __init__(self, message, long_message=None, description=None):
        AssertionError.__init__(self, message)
        self.message = message
        self.long_message = long_message
        self.description = description

    def __str__(self):
        result = []
        if self.description is not None:
            result.append( "[%s]" % self.description )
        result.append( self.message )
        if self.long_message is not None:
            result.append( "----- long message -----" )
            result.append(self.long_message)
        return "\n".join(result)

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

    p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate(input)
    return stdout, stderr, p.returncode

def _normalize_newlines(string):
    import re
    return re.sub(r'(\r\n|\r|\n)', '\n', string)

def assert_true(condition, msg=None):
    if condition: return
    if msg is None:
        msg = "condition not true"
    raise TestoobAssertionError(msg, description="assert_true failed")

def assert_equals(expected, actual, msg=None, filter=None):
    "works like unittest.TestCase.assertEquals"
    if filter is not None:
        actual = filter(actual)

    if expected == actual: return
    if msg is None:
        msg = '%s != %s' % (expected, actual)
    raise TestoobAssertionError(msg, description="assert_equals failed")

def assert_matches(regex, actual, msg=None, filter=None):
    "fail unless regex matches actual (using re.search)"
    import re
    if filter is not None:
        actual = filter(actual)

    if re.search(regex, actual, re.DOTALL) is not None: return

    if msg is None:
        msg = "'%(actual)s' doesn't match regular expression '%(regex)s'" % vars()
    raise TestoobAssertionError(msg, description="assert_matches failed")

def _call_signature(callable, *args, **kwargs):
    """
    Generate a human-friendly call signature

    From recipe http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/307970
    """
    argv = [repr(arg) for arg in args] + ["%s=%r" % x for x in kwargs.items()]
    return "%s(%s)" % (callable.__name__, ", ".join(argv))

def assert_raises(exception_class, callable, *args, **kwargs):
    """
    Assert that a callable raises an exception, similar to unittest.py's
    assertRaises.

    Takes more ideas and code from recipe
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/307970
    """
    from testoob.utils import _pop
    expected_args = _pop(kwargs, "expected_args", None)
    expected_regex = _pop(kwargs, "expected_regex", None)

    def callsig():
        return _call_signature(callable, *args, **kwargs)

    try:
        callable(*args, **kwargs)
    except exception_class, e:
        if expected_args is not None:
            assert_equals(
                expected_args, e.args,
                msg="%s raised %s with unexpected args: expected=%r, actual=%r" % (callsig(), e.__class__, expected_args, e.args)
            )
        if expected_regex is not None:
            assert_matches(
                expected_regex, str(e),
                msg="%s raised %s, but the regular expression '%s' doesn't match %r" % (callsig(), e.__class__, expected_regex, str(e))
            )
    else:
        excName = getattr(exception_class, "__name__", str(exception_class))
        raise TestoobAssertionError(
            "%s not raised" % excName, description="assert_raises failed")

def command_line(
        args,
        input=None,
        expected_output=None,
        expected_error=None,
        expected_output_regex=None,
        expected_error_regex=None,
        expected_rc=None,
        rc_predicate=None,
    ):

    # run command
    output, error, rc = _run_command(args, input)

    # test
    try:
        if expected_error is not None:
            assert_equals(expected_error, error, filter=_normalize_newlines)
        if expected_output is not None:
            assert_equals(expected_output, output, filter=_normalize_newlines)
        if expected_output_regex is not None:
            assert_matches(expected_output_regex, output, filter=_normalize_newlines)
        if expected_error_regex is not None:
            assert_matches(expected_error_regex, error, filter=_normalize_newlines)
        if expected_rc is not None:
            assert_equals(expected_rc, rc)
        if rc_predicate is not None:
            assert_true(rc_predicate(rc))
    except TestoobAssertionError, e:
        assert e.long_message is None
        def annotated_err_string(name, value):
            if not value: return "== %s: NONE" % name
            import re
            annotation_pattern = re.compile("^", re.MULTILINE)
            annotated_value = annotation_pattern.sub("%s: "%name, value)
            return "== %s\n%s" % (name, annotated_value)
        e.long_message = "\n".join([
            "command_line test failed",
            "== args: %s" % args,
            "== rc: %s" % rc,
            annotated_err_string("stdout", output),
            annotated_err_string("stderr", error),
        ])
        raise

def skip(reason="No reason given"):
    "Skip this test"
    from testoob import SkipTestException
    raise SkipTestException(reason)
