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

"test running logic"

import unittest as _unittest
from testoob.extracting import suite_iter as _suite_iter

###############################################################################
# apply_runner
###############################################################################
from testoob.extracting import full_extractor as _full_extractor

def apply_decorators(callable, decorators):
    "Wrap the callable in all the decorators"
    result = callable
    for decorator in decorators:
        result = decorator(result)
    return result

def apply_runner(suites, runner, interval=None, stop_on_fail=False,
                 extraction_decorators = None, timeout=0):
    """Runs the suite."""
    if extraction_decorators is None: extraction_decorators = []
    test_extractor = apply_decorators(_full_extractor, extraction_decorators)

    class Alarmed_fixture:
        def __init__(self, fixture):
            self.alarm = lambda x:x
            if timeout:
                from signal import alarm
                self.alarm = alarm
            self.fixture = fixture
        
        def __call__(self, *args):
            self.alarm(timeout) # Set timeout for a fixture.
            self.fixture(*args)
            self.alarm(0) # Release the alarm that was set.

        def get_fixture(self):
            return self.fixture
    
    def running_loop():
        import time
        first = True
        for suite in _suite_iter(suites):
            for fixture in test_extractor(suite):
                if not first and interval is not None:
                    time.sleep(interval)
                first = False
                if not runner.run(Alarmed_fixture(fixture)) and stop_on_fail:
                    return

    running_loop()
    runner.done()
    return runner.isSuccessful()

###############################################################################
# Runners
###############################################################################

class BaseRunner(object):
    """default implementations of setting a reporter and done()"""
    def __init__(self):
        from testoob.asserter import Asserter
        self._Asserter = Asserter

    def _set_reporter(self, reporter):
        self._reporter = reporter
        self._reporter.start()
    reporter = property(lambda self:self._reporter, _set_reporter)

    def run(self, fixture):
        # Let the assert functions know it's reporter.
        self._Asserter().set_reporter(fixture.get_fixture(), self._reporter)

    def done(self):
        self.reporter.done()

    def isSuccessful(self):
        return self.reporter.isSuccessful()

class SimpleRunner(BaseRunner):
    def run(self, fixture):
        BaseRunner.run(self, fixture)
        fixture(self._reporter)
        return self._reporter.isSuccessful()

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
        BaseRunner.run(self, fixture)
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
        BaseRunner.run(self, fixture)
        self._helper.register_fixture(fixture)

    def done(self):
        self._helper.start(self.reporter)
        BaseRunner.done(self)

class _TestHistory:
    def __init__(self):
        self.modules = {}

    def record_fixture(self, fixture):
        """Store the info about each fixture, to show them later.
        """
        from testoob.reporting import TestInfo
        fixture_info = TestInfo(fixture)
        self._class_function_list(fixture_info).append(fixture_info.funcinfo())

    def get_string(self, max_functions_to_show):
        """Show the test methods, if there are too many list the classes only.
        """
        result = []
        for (module_name, module_info) in self.modules.items():
            result.append("Module: %s (%s)" % \
                    (module_name, module_info["filename"]))
            for (class_name, functions) in module_info["classes"].items():
                result.append("\tClass: %s (%d test functions)" %\
                      (class_name, len(functions)))
                if self._num_functions() <= max_functions_to_show:
                    for func in functions:
                        result.append("\t\t%s()%s" % \
                                (func[0], func[1] and " - "+func[1] or ""))
        return "\n".join(result)

    def _module(self, fixture_info):
        self.modules.setdefault(
                fixture_info.module(),
                {
                    "filename": fixture_info.filename(),
                    "classes": {}
                })
        return self.modules[fixture_info.module()]

    def _class_function_list(self, fixture_info):
        classes_dict = self._module(fixture_info)["classes"]
        classes_dict.setdefault(fixture_info.classname(), [])
        return classes_dict[fixture_info.classname()]

    def _num_functions(self):
        result = 0
        for mod_info in self.modules.values():
            for functions in mod_info["classes"].values():
                result += len(functions)
        return result

class ListingRunner(BaseRunner):
    """Just list the test names, don't run them.
    """
    
    def __init__(self):
        self.history = _TestHistory()

    def run(self, fixture):
        self.history.record_fixture(fixture.get_fixture())

    def done(self):
        print self.history.get_string(max_functions_to_show=50)

# Distributed runner using Pyro
from pyro_runner import PyroRunner

def run(suite=None, suites=None, **kwargs):
    "Convenience frontend for text_run_suites"
    if suite is None and suites is None:
        raise TypeError("either suite or suites must be specified")
    if suite is not None and suites is not None:
        raise TypeError("only one of suite or suites may be specified")

    if suites is None:
        suites = [suite]

    return run_suites(suites, **kwargs)

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
    from testoob.reporting import ReporterProxy
    result = ReporterProxy()
    for reporter in reporters:
        result.add_observer(_apply_debug(reporter, runDebug))
    return result

def run_suites(suites, reporters, runner=None, runDebug=None, **kwargs):
    "Run the test suites"
    runner = runner or SimpleRunner()
    runner.reporter = _create_reporter_proxy(reporters, runDebug)
    
    return apply_runner(suites=suites,
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

    import sys
    from testoob.reporting import TextStreamReporter
    reporter_class = _pop(kwargs, "reporter_class", TextStreamReporter)

    reporter_instance = reporter_class(
            verbosity=verbosity,
            immediate=immediate,
            descriptions=1,
            stream=sys.stderr)

    kwargs["reporters"].append(reporter_instance)

    return run(*args, **kwargs)

