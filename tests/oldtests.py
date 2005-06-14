import helpers
helpers.fix_include_path()

import sys
import testoob

import suites
from suites import CaseDigits, CaseLetters

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

def check(expected, actual):
    if expected is None: return
    if type(expected) == type([]):
        expected.sort()
        actual.sort()
    if expected != actual:
        print "[x] check failed, expected=%(expected)s, actual=%(actual)s" % vars()

def helper_run(code,
    verbose=False,
    expected_successes=None,
    expected_errors=None,
    expected_failures=None,
    expected_stdout=None,
    expected_stderr=None):

    from suites import run_log
    run_log.clear()

    run_log.stdout, run_log.stderr = capture_output(code)

    check(expected_successes, run_log.successes)
    check(expected_errors,    run_log.errors)
    check(expected_failures,  run_log.failures)
    check(expected_stdout,    run_log.stdout)
    check(expected_stderr,    run_log.stderr)
    if verbose:
        print "stdout:"
        print run_log.stdout
        print "stderr:"
        print run_log.stderr

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
    return suites.suite()

def test_main_noargs():
    helper_main_with_args(
        expected_successes = suites.all_test_names)

def test_main_verbose():
    helper_main_with_args("-v", expected_successes = suites.all_test_names)

def test_main_quiet():
    helper_main_with_args("-q", expected_successes = suites.all_test_names)

def test_main_regex():
    helper_main_with_args("--regex=1|B", expected_successes = ["testB", "test1"])

def test_main_interval():
    import time
    interval_to_test = 0.01
    start_time = time.time()
    helper_main_with_args("--interval=%f" % interval_to_test, expected_successes = suites.all_test_names)
    tests_time = time.time() - start_time
    should_take = (interval_to_test * len(suites.all_test_names))
    if not (should_take + 0.5) > tests_time > should_take:
        check(should_take, tests_time)

def helper_run_mixed(**kwargs):
    helper_run(lambda : testoob.main(suite=suites.CaseMixed.suite()),
            **kwargs)

def test_main_error():
    helper_run_mixed(expected_errors=["testError"])

def test_main_failure():
    helper_run_mixed(expected_failures=["testFailure"])

def test_main_success():
    helper_run_mixed(expected_errors=["testSuccess"])

def test_main_suite():
    helper_run(lambda : testoob.main(suite=suites.suite()))

def test_main_defaultTest():
    helper_run(lambda : testoob.main(defaultTest="suite"), expected_successes = suites.all_test_names)

if __name__ == "__main__":
    for name, value in globals().items():
        if name.startswith("test_") and callable(value):
            print >>sys.stderr, "*", name
            value()
