# TestOOB, Python Testing Out Of (The) Box
# Copyright (C) 2005 The TestOOB Team
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

def assert_equals(expected, actual, msg=None, filter=None):
    "works like unittest.TestCase.assertEquals"
    if filter is not None:
        actual = filter(actual)

    if expected == actual: return
    if msg is None:
        msg = '%s != %s' % (expected, actual)
    raise AssertionError(msg)

def assert_matches(regex, actual, msg=None, filter=None):
    "fail unless regex matches actual (using re.search)"
    import re
    if filter is not None:
        actual = filter(actual)

    if re.search(regex, actual, re.DOTALL) is not None: return

    if msg is None:
        msg = "'%(actual)s' doesn't match regular expression '%(regex)s'" % vars()
    raise AssertionError(msg)

def assert_raises(exception_class, callable, *args, **kwargs):
    "Code similar to unittest.py's assertRaises"
    try:
        callable(*args, **kwargs)
    except exception_class:
        pass
    else:
        excName = getattr(exception_class, "__name__", str(exception_class))
        raise AssertionError("%s not raised" % excName)

def conditionally_assert_equals(expected, actual, **kwargs):
    "assert_equals only if expected is not None"
    if expected is not None:
        assert_equals(expected, actual, **kwargs)

def conditionally_assert_matches(expected_regex, actual, **kwargs):
    "assert_matches only if expected_regex is not None"
    if expected_regex is not None:
        assert_matches(expected_regex, actual, **kwargs)

def command_line(
        args,
        input=None,
        expected_output=None,
        expected_error=None,
        expected_output_regex=None,
        expected_error_regex=None,
        expected_rc=None,
    ):

    # TODO: make errors print full status like working directory, etc.

    # run command
    output, error, rc = _run_command(args, input)

    # test
    conditionally_assert_equals(expected_error, error, filter=_normalize_newlines)
    conditionally_assert_equals(expected_output, output, filter=_normalize_newlines)
    conditionally_assert_matches(expected_output_regex, output, filter=_normalize_newlines)
    conditionally_assert_matches(expected_error_regex, error, filter=_normalize_newlines)
    conditionally_assert_equals(expected_rc, rc)
