import unittest as _unittest

###############################################################################
# apply_runner
###############################################################################
from extractors import extract_fixtures as _extract_fixtures
def apply_runner(suites, runner, reporter, test_extractor=None):
    """Runs the suite."""
    if test_extractor is None: test_extractor = _extract_fixtures

    runner.set_result(reporter)

    reporter.start()
    for suite in suites:
        for fixture in test_extractor(suite):
            runner.run(fixture)
    reporter.done()

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
    def __init__(self):
        self._result = None

    def run(self, fixture):
        fixture(self._result)

    def set_result(self, result):
        self._result = result

###############################################################################
# text_run
###############################################################################

def text_run(suite=None, suites=None, **kwargs):
    "Convenience frontend for text_run_suites"
    if suite is None and suites is None:
        raise TypeError("either suite or suites must be specified")
    if suite is not None and suites is not None:
        raise TypeError("only one of suite or suites may be specified")

    if suites is None:
        suites = [suite]

    text_run_suites(suites, **kwargs)


def text_run_suites(suites, runner_class=SimpleRunner, verbosity=1,
                    test_extractor=None):
    "Run suites and generate output similar to unittest.TextTestRunner's"

    import sys
    from reporting import TextStreamReporter
    apply_runner(suites=suites,
                 runner=runner_class(),
                 reporter=TextStreamReporter(verbosity=verbosity,
                                             descriptions=1,
                                             stream=sys.stderr),
                 test_extractor=test_extractor)

