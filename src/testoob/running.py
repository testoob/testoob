import unittest as _unittest

###############################################################################
# apply_runner
###############################################################################
from extractors import extract_fixtures as _extract_fixtures
import time
def apply_runner(suites, runner, reporter, interval, test_extractor=None):
    """Runs the suite."""
    if test_extractor is None: test_extractor = _extract_fixtures

    runner.set_result(reporter)

    reporter.start()
    first = True
    for suite in suites:
        for fixture in test_extractor(suite):
            if not first:
                time.sleep(interval)
            first = False
            runner.run(fixture)
    reporter.done()

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

def run(suite=None, suites=None, **kwargs):
    "Convenience frontend for text_run_suites"
    if suite is None and suites is None:
        raise TypeError("either suite or suites must be specified")
    if suite is not None and suites is not None:
        raise TypeError("only one of suite or suites may be specified")

    if suites is None:
        suites = [suite]

    run_suites(suites, **kwargs)

def run_suites(suites, reporters, runner_class=SimpleRunner, **kwargs):
    "Run the test suites"

    from reporting import ReporterProxy
    reporter_proxy = ReporterProxy()
    for reporter in reporters:
        reporter_proxy.add_observer(reporter)

    apply_runner(suites=suites,
                 runner=runner_class(),
                 reporter=reporter_proxy,
                 **kwargs)

###############################################################################
# text_run
###############################################################################

def text_run(*args, **kwargs):
    """
    Run suites with a TextStreamReporter.
    Accepts keyword 'verbosity' (0, 1, or 2, default is 1)
    """

    verbosity = kwargs.pop("verbosity", 1)

    kwargs.setdefault("reporters", [])

    import sys, reporting
    reporter_class = kwargs.pop("reporter_class", reporting.TextStreamReporter)
    kwargs["reporters"].append( reporter_class(
            verbosity=verbosity,
            descriptions=1,
            stream=sys.stderr) )

    run(*args, **kwargs)



