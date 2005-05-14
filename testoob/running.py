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
                    reporters = [], **kwargs):
    "Run suites and generate output similar to unittest.TextTestRunner's"

    from reporting import ReporterProxy, TextStreamReporter
    import sys
    reporter_proxy = ReporterProxy()
    reporter_proxy.add_observer(
            TextStreamReporter(verbosity=verbosity,
                               descriptions=1,
                               stream=sys.stderr))

    for reporter in reporters:
        reporter_proxy.add_observer(reporter)

    apply_runner(suites=suites,
                 runner=runner_class(),
                 reporter=reporter_proxy,
                 **kwargs)
