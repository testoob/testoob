# Fix path to use development version
import sys, os
sys.path.insert(0, os.path.join(os.path.basename(sys.argv[0]), ".."))

import testoob

import regular_suite
from regular_suite import CaseDigits, CaseLetters

def capture_output(code):
    from cStringIO import StringIO
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()

    try:
        code()
    finally:
        out = sys.stdout.getvalue()
        err = sys.stderr.getvalue()
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    return out, err

def list_equals(a, b):
    a.sort()
    b.sort()
    assert a == b

def helper_run(code, expected_successes=None):

    from regular_suite import run_log
    run_log.clear()

    run_log.stdout, run_log.stderr = capture_output(code)

    if expected_successes: list_equals(expected_successes, run_log.successes)

def helper_main_with_args(*args, **kwargs):
    old_argv = sys.argv
    import copy
    sys.argv = copy.copy(old_argv)
    sys.argv.extend(args)

    try:
        helper_run(testoob.main, **kwargs)
    finally:
        sys.argv = old_argv

def suite():
    return regular_suite.suite()

def test_main_noargs():
    helper_main_with_args(
        expected_successes = regular_suite.all_test_names)

def test_main_verbose():
    helper_main_with_args("-v", expected_successes = regular_suite.all_test_names)

def test_main_quiet():
    helper_main_with_args("-q", expected_successes = regular_suite.all_test_names)

def test_main_regex():
    helper_main_with_args("--regex=1|B", expected_successes = ["testB", "test1"])

def test_main_suite():
    helper_run(lambda : testoob.main(suite=regular_suite.suite()))

def test_main_defaultTest():
    helper_run(lambda : testoob.main(defaultTest="suite"), expected_successes = regular_suite.all_test_names)

if __name__ == "__main__":
    for name, value in globals().items():
        if name.startswith("test_") and callable(value):
            print >>sys.stderr, "*", name
            value()
