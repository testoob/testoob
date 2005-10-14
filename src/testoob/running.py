# TestOOB, Python Testing Out Of (The) Box
# Copyright (C) 2005 Ori Peleg, Barak Schiller, and Misha Seltzer
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

"test running logic"

import unittest as _unittest
from extracting import suite_iter as _suite_iter

###############################################################################
# apply_runner
###############################################################################
from extracting import full_extractor as _full_extractor
import time

def apply_decorators(callable, decorators):
    "Wrap the callable in all the decorators"
    result = callable
    for decorator in decorators:
        result = decorator(result)
    return result

def apply_runner(suites, runner, interval=None, extraction_decorators = None):
    """Runs the suite."""

    if extraction_decorators is None: extraction_decorators = []
    test_extractor = apply_decorators(_full_extractor, extraction_decorators)

    first = True
    for suite in _suite_iter(suites):
        for fixture in test_extractor(suite):
            if not first and interval is not None:
                time.sleep(interval)
            first = False
            runner.run(fixture)
    runner.done()

###############################################################################
# Runners
###############################################################################

class BaseRunner(object):
    """default implementations of setting a reporter and done()"""
    def _set_reporter(self, reporter):
        self._reporter = reporter
        self._reporter.start()
    reporter = property(lambda self:self._reporter, _set_reporter)

    def run(self, fixture):
        # just to remind you :-)
        raise NotImplementedError

    def done(self):
        self.reporter.done()

class SimpleRunner(BaseRunner):
    def run(self, fixture):
        fixture(self._reporter)

class ThreadedRunner(BaseRunner):
    """Run tests using a threadpool.
    Uses TwistedPython's thread pool"""
    def __init__(self, max_threads=None):
        BaseRunner.__init__(self)

        from twisted.python.threadpool import ThreadPool

        min_threads = min(ThreadPool.min, max_threads)
        self.pool = ThreadPool(minthreads = min_threads, maxthreads=max_threads)
        self.pool.start()

    def run(self, fixture):
        self.pool.dispatch(None, fixture, self.reporter)

    def done(self):
        self.pool.stop()
        BaseRunner.done(self)

class ProcessedRunner(BaseRunner):
    "Run tests using fork in different processes."
    def __init__(self, max_processes=1):
        from processed_helper import ProcessedRunnerHelper
        BaseRunner.__init__(self)
        self._helper = ProcessedRunnerHelper(max_processes)

    def run(self, fixture):
        self._helper.register_fixture(fixture)

    def done(self):
        self._helper.start(self.reporter)
        BaseRunner.done(self)

def run(suite=None, suites=None, **kwargs):
    "Convenience frontend for text_run_suites"
    if suite is None and suites is None:
        raise TypeError("either suite or suites must be specified")
    if suite is not None and suites is not None:
        raise TypeError("only one of suite or suites may be specified")

    if suites is None:
        suites = [suite]

    run_suites(suites, **kwargs)

def _apply_debug(reporter, runDebug):
    if runDebug is None:
        return reporter

    def replace(reporter, flavor, methodname):
        original = getattr(reporter, methodname)
        def replacement(test, err):
            runDebug(test, err, flavor, reporter, original)
        setattr(reporter, methodname, replacement)

    replace(reporter, "error", "addError")
    replace(reporter, "failure", "addFailure")

    return reporter

def _create_reporter_proxy(reporters, runDebug):
    from reporting import ReporterProxy
    result = ReporterProxy()
    for reporter in reporters:
        result.add_observer(_apply_debug(reporter, runDebug))
    return result

def run_suites(suites, reporters, runner=None, runDebug=None, **kwargs):
    "Run the test suites"
    runner = runner or SimpleRunner()
    runner.reporter = _create_reporter_proxy(reporters, runDebug)

    apply_runner(suites=suites,
                 runner=runner,
                 **kwargs)

###############################################################################
# text_run
###############################################################################

def _pop(d, key, default):
    try:
        return d.pop(key, default)
    except AttributeError:
        pass

    # In Python 2.2 we'll implement pop ourselves
    try:
        return d.get(key, default)
    finally:
        if key in d: del d[key]

def text_run(*args, **kwargs):
    """
    Run suites with a TextStreamReporter.
    Accepts keyword 'verbosity' (0, 1, 2 or 3, default is 1)
    and 'immediate' (True or False)
    """

    verbosity = _pop(kwargs, "verbosity", 1)
    immediate = _pop(kwargs, "immediate", False)

    kwargs.setdefault("reporters", [])

    import sys, reporting
    reporter_class = _pop(kwargs, "reporter_class", reporting.TextStreamReporter)

    reporter_instance = reporter_class(
            verbosity=verbosity,
            immediate=immediate,
            descriptions=1,
            stream=sys.stderr)

    if verbosity == 3:
        import verbalize
        verbalize.make_methods_verbose("unittest",
                                       "TestCase",
                                       "(^assert)|(^fail[A-Z])|(^fail$)",
                                       reporter_instance)

    kwargs["reporters"].append(reporter_instance)

    run(*args, **kwargs)
    return reporter_instance.getDoneStatus()

