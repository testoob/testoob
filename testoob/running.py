import unittest as _unittest

###############################################################################
# apply_runner
###############################################################################
def apply_runner(suites, runner, test_extractor=None):
    """Runs the suite."""
    if test_extractor is None:
        from extractors import extract_fixtures
        test_extractor = extract_fixtures

    for suite in suites:
        for fixture in test_extractor(suite):
            runner.run(fixture)

###############################################################################
# results proxy
###############################################################################
def ObserverProxy(method_names):
    class Proxy:
        def __init__(self):
            self._observers = []
        def add_observer(self, observer):
            self._observers.append(observer)
        def remove_observer(self, observer):
            self._observers.remove(observer)

    def create_method_proxy(method_name):
        def method_proxy(self, *args, **kwargs):
            for observer in self._observers:
                getattr(observer, method_name)(*args, **kwargs)
        return method_proxy
            
    for method_name in method_names:
        setattr(Proxy, method_name, create_method_proxy(method_name))

    return Proxy

ProxyingTestResult = ObserverProxy([
    "startTest", "stopTest", "addError", "addFailure", "addSuccess"
])


###############################################################################
# Runners
###############################################################################

class SimpleRunner:
    def __init__(self, results = []):
        self._result = ProxyingTestResult()
        for result in results:
            self.add_result(result)

    def run(self, fixture):
        fixture(self._result)

    def add_result(self, result):
        self._result.add_observer(result)

###############################################################################
# text_run
###############################################################################

def _print_results(result, timeTaken):
    # code modified from Python 2.4's standard unittest module
    stream = result.stream
    result.printErrors()
    stream.writeln(result.separator2)
    run = result.testsRun
    stream.writeln("Ran %d test%s in %.3fs" %
                   (run, run != 1 and "s" or "", timeTaken))
    stream.writeln()
    if not result.wasSuccessful():
        stream.write("FAILED (")
        failed, errored = map(len, (result.failures, result.errors))
        if failed:
            stream.write("failures=%d" % failed)
        if errored:
            if failed: stream.write(", ")
            stream.write("errors=%d" % errored)
        stream.writeln(")")
    else:
        stream.writeln("OK")

def text_run(suite=None, suites=None, runner_class=SimpleRunner, verbosity=1,
             test_extractor=None):
    "Run a suite and generate output similar to unittest.TextTestRunner's"

    if suite is None and suites is None:
        raise TypeError("either suite or suites must be specified")
    if suite is not None and suites is not None:
        raise TypeError("only one of suite or suites may be specified")

    if suites is None:
        suites = [suite]

    import sys
    class MyTextTestResult(_unittest._TextTestResult):
        def __init__(self):
            _unittest._TextTestResult.__init__(self,
                         verbosity=verbosity,
                         descriptions=1,
                         stream=_unittest._WritelnDecorator(sys.stderr))

    import time
    result = MyTextTestResult()
    runner = runner_class(results = [result])

    start = time.time()
    apply_runner(suites=suites, runner=runner, test_extractor=test_extractor)
    timeTaken = time.time() - start
    
    _print_results(result, timeTaken)


