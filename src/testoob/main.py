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

"main() implementation"

import os, sys

try:
    set
except NameError:
    try:
        # Python 2.3 compatibility
        from sets import Set as set
    except ImportError:
        # Python 2.2 compatibility
        from compatibility.sets import Set as set

import commandline
import testoob.reporting

def _arg_parser():
    p = commandline.parsing.parser

    p.add_option("-q", "--quiet",   action="store_true", help="Minimal output")
    p.add_option("-v", "--verbose", action="store_true", help="Verbose output")
    p.add_option("--vassert", action="store_true", help="Make asserts verbose")
    p.add_option("--interval", metavar="SECONDS", type="float", default=0, help="Add interval between tests")
    p.add_option("--timeout", metavar="SECONDS", type="int", help="Fail test if passes timeout")
    p.add_option("--timeout-with-threads", metavar="SECONDS", type="float", help="Fail test if passes timeout, implemented with threads")
    p.add_option("--stop-on-fail", action="store_true", help="Stop tests on first failure")
    p.add_option("--debug", action="store_true", help="Run pdb on tests that fail")
    p.add_option("--threads", metavar="NUM_THREADS", type="int", help="Run in a threadpool")
    p.add_option("--capture", action="store_true", help="Capture the output of the test, and show it only if test fails")
    coverage_choices = ["silent", "slim", "normal", "massive", "xml"]
    p.add_option("--coverage", metavar="AMOUNT", type="choice", choices=coverage_choices, help="Test the coverage of the tested code, choices are: %s" % coverage_choices)
    p.add_option("--test-method-glob", metavar="PATTERN", help="Collect test methods based on a glob pattern")
    p.add_option("--test-method-regex", metavar="REGEX", help="Collect test methods based on a regular expression")
    profiler_choices = ["hotshot", "profile"]
    p.add_option("--profiler", type="choice", choices=profiler_choices, help="Profile the tests with a profiler, choices are: %s" % profiler_choices)
    p.add_option("--profdata", metavar="FILE", default="testoob.stats", help="Target file for profiling information, default is '%default'")
    p.add_option("--rerun-on-fail", action="store_true", help="Used with --debug, rerun a failing test when debugging it")

    return p

def _get_verbosity(options):
    if options.quiet: return 0
    if options.vassert: return 3
    if options.verbose: return 2
    return 1

def _get_suites(suite, defaultTest, test_names, test_loader=None):
    if suite is not None:
        # an explicit suite always wins
        return [suite]

    if test_loader is None:
        import unittest
        test_loader = unittest.TestLoader()

    import __main__
    if len(test_names) == 0 and defaultTest is None:
        # load all tests from __main__
        return test_loader.loadTestsFromModule(__main__)

    if len(test_names) == 0:
        test_names = [defaultTest]

    # Don't repeat tests
    test_names = set(test_names)

    try:
        return test_loader.loadTestsFromNames(test_names, __main__)
    except AttributeError, e:
        def testName(exception):
            import re
            mo = re.search("has no attribute '([^']+)'", str(e))
            assert mo is not None
            return mo.group(1)
        import sys
        print >>sys.stderr, "ERROR: Can't find test case '%s'" % testName(e)
        sys.exit(1)

def _dirname_from_func(func):
    return os.path.dirname(func.func_code.co_filename)

def _coverage_ignore_paths():
    # Ignore coverage from the 'testoob' library (where this file is), and
    # from the python system library (assuming 'os' module placed there).

    # Getting the directory name from functions instead of __file__ so it
    # will work with soft links to the actual modules.
    testoob_dirname = _dirname_from_func(_coverage_ignore_paths)
    python_dirname = _dirname_from_func(os.getenv)
    return (testoob_dirname, python_dirname)

from commandline.parsing import ArgumentsError

def _main(suite, defaultTest, options, test_names, parser):

    from commandline.parsing import require_posix, require_modules

    def conflicting_options(*option_names):
        given_options = [
            name
            for name in option_names
            if getattr(options, name) is not None
        ]
        given_options.sort()

        if len(given_options) > 1:
            raise ArgumentsError(
                    "The following options can't be specified together: %s" %
                    ", ".join(given_options))

    conflicting_options("threads", "timeout")
    conflicting_options("timeout", "timeout_with_threads")
    conflicting_options("threads", "processes", "processes_old", "processes_pyro", "stop_on_fail")
    conflicting_options("threads", "processes", "processes_old", "processes_pyro", "list") # specify runners
    conflicting_options("processes", "processes_old", "processes_pyro", "debug")
    conflicting_options("capture", "list")

    testoob.reporting.options.verbosity = _get_verbosity(options)
    commandline.parsing.kwargs = {
        "stop_on_fail" : options.stop_on_fail,
        "reporters" : [],
        "extraction_decorators" : [],
        "fixture_decorators" : [],
        "interval" : options.interval,
    }
    kwargs = commandline.parsing.kwargs # TODO: convert to calls to commandline.parsing.kwargs

    for processor in commandline.parsing.option_processors:
        processor(options)

    def get_test_loader():
        if options.test_method_regex is not None:
            from test_loaders import RegexLoader
            return RegexLoader(options.test_method_regex)
        if options.test_method_glob is not None:
            from test_loaders import GlobLoader
            return GlobLoader(options.test_method_glob)
        return None # use the default

    kwargs["suites"] = _get_suites(
        suite, defaultTest, test_names, test_loader=get_test_loader())
    
    if options.coverage is not None:
        from running import fixture_decorators
        from coverage import Coverage
        cov = Coverage(_coverage_ignore_paths())
        kwargs["fixture_decorators"].append(
                fixture_decorators.get_coverage_fixture(cov))
        if options.coverage != "silent":
            testoob.reporting.options.coverage = (options.coverage, cov)
    
    if options.capture is not None:
        from running import fixture_decorators
        kwargs["fixture_decorators"].append(
                fixture_decorators.get_capture_fixture())

    if options.vassert:
        import asserter
        asserter.register_asserter()
    
    if options.timeout is not None:
        require_posix("--timeout")
        from running import fixture_decorators
        kwargs["fixture_decorators"].append(
            fixture_decorators.get_alarmed_fixture(options.timeout))
        def alarm(sig, stack_frame):
            raise AssertionError("Timeout")
        import signal
        signal.signal(signal.SIGALRM, alarm)

    if options.timeout_with_threads is not None:
        import thread
        if not hasattr(thread, "interrupt_main"):
            raise ArgumentsError("Older versions of Python don't support thread.interrupt_main")
        from running import fixture_decorators
        kwargs["fixture_decorators"].append(
            fixture_decorators.get_thread_timingout_fixture(options.timeout_with_threads))

    if options.rerun_on_fail is not None:
        if options.debug is None:
            raise ArgumentsError("--rerun-on-fail requires --debug")

    if options.debug is not None:
        import pdb
        def runDebug(test, err_info, flavour, reporter, real_add):
            if options.timeout is not None:
                from signal import alarm
                alarm(0) # Don't timeout on debug.
            assert flavour in ("error", "failure")
            real_add(test, err_info)
            print "\nDebugging for %s in test: %s" % (
                    flavour, reporter.getDescription(test))
            if options.rerun_on_fail is not None:
                #test.funcname will be our current test function
                #use that to get the function object for our method
                #and call it manually. WD-rpw 10-31-06
                methodName = test.funcname()
                method = getattr( test.fixture,  methodName)
                print "rerunning test for failed %s()" % (methodName)
                try:
                    pdb.runcall( method )
                except:
                    pdb.post_mortem( err_info.traceback() )
            else:
                pdb.post_mortem(err_info.traceback())
                
        kwargs["runDebug"] = runDebug

    if options.threads is not None:
        from running import ThreadedRunner
        kwargs["runner"] = ThreadedRunner(num_threads = options.threads)
        kwargs["threads"] = True

    if options.profiler is not None:
        # this module is sometimes missing, apparently its license is a problem
        # for some OS distributions
        require_modules("--profiler", "profile")

    def text_run_decorator():
        if options.profiler is not None:
            import profiling
            return profiling.profiling_decorator(
                options.profiler, options.profdata)

        # return a null decorator
        return lambda x: x

    # apply the decorator to running.text_run
    import running
    return text_run_decorator()(running.text_run)(**kwargs)

def kwarg_to_option(arg, value):
    cmdarg = arg.replace("_", "-")
    if value is True:
        return "--%s" % cmdarg
    else:
        return "--%s=%s" % (cmdarg, value)

def _config_file_args():
    filename = os.path.expanduser("~/.testoobrc")
    if not os.path.exists(filename):
        return [] # No config file

    import ConfigParser
    try:
        config = ConfigParser.ConfigParser()
        config.read(filename)

        result = []
        for option in config.options("default"):
            value = config.get("default", option)
            if value.lower() in ("true", "false"):
                if value.lower() == "true":
                    result.append("--%s" % option)
            else:
                result.append("--%s=%s" % (option, value))

        return result
    except ConfigParser.Error, e:
        import warnings
        warnings.warn("Error reading config file: %s" % e)
        return []

def _parse_args():
    args = _config_file_args() + sys.argv[1:]

    parser = _arg_parser()
    options, args = parser.parse_args(args)
    return parser, options, args

def main(suite=None, defaultTest=None, **kwargs):
    import sys
    for arg, value in kwargs.items():
        sys.argv.append(kwarg_to_option(arg, value))
    
    parser, options, test_names = _parse_args()

    try:
        sys.exit(not _main(suite, defaultTest, options, test_names, parser))
    except ArgumentsError, e:
        parser.error(str(e))

