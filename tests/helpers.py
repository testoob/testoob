def project_subpath(*components):
    from os.path import dirname, join, normpath
    return normpath(join(dirname(__file__), "..", *components))

def module_path():
    return project_subpath("src")

def executable_path():
    return project_subpath("src", "testoob", "testoob")

def fix_include_path():
    import sys
    if module_path() not in sys.path:
        sys.path.insert(0, module_path())

fix_include_path()

# TODO: subclass testoob.reporting.BaseReporter, implements most of the methods here
class ReporterWithMemory:
    "A reporter that remembers info on the test fixtures run"
    def __init__(self):
        self.started = []
        self.successes = []
        self.errors = []
        self.failures = []
        self.finished = []
        self.asserts = {}
        self.stdout = ""
        self.stderr = ""

        self.has_started = False
        self.is_done = False

    def _append_test(self, l, test_info):
        # TODO: use test_info.methodname()
        l.append(str(test_info).split()[0])

    def setParameters(self, **parameters):
        pass # TODO: placeholder
    def start(self):
        self.has_started = True
    def done(self):
        self.is_done = True
    def startTest(self, test_info):
        self._append_test(self.started, test_info)
    def stopTest(self, test_info):
        self._append_test(self.finished, test_info)
    def addError(self, test_info, err_info):
        self._append_test(self.errors, test_info)
    def addFailure(self, test_info, err_info):
        self._append_test(self.failures, test_info)
    def addSuccess(self, test_info):
        self._append_test(self.successes, test_info)
    def addAssert(self, test_info, assertName, varList, exception):
        self.asserts[str(test_info).split()[0]] = (assertName, exception.__class__)
    def isSuccessful(self):
        pass

    def __str__(self):
        attrs = ("started","successes","errors","failures","finished","stdout","stderr")
        return "\n".join(["%s = %s" % (attr, getattr(self,attr)) for attr in attrs])

class TestoobRunnerWithMemory:
    def __init__(self):
        self.reporter = ReporterWithMemory()

    def run(self, **kwargs):
        testoob.running.run(reporters=[self.reporter], **kwargs)

    def check_reporter(self, **kwargs):
        for attr, expected in kwargs.items():
            actual = getattr(self.reporter, attr)
            if type(expected) == type([]):
                expected.sort()
                actual.sort()
            from testoob.testing import assert_equals
            assert_equals(expected, actual)

import unittest
import testoob.running
class TestoobBaseTestCase(unittest.TestCase):
    def setUp(self):
        self.runner = TestoobRunnerWithMemory()
    def tearDown(self):
        del self.runner
    def _check_reporter(self, **kwargs):
        self.runner.check_reporter(**kwargs)
    def _run(self, **kwargs):
        self.runner.run(**kwargs)

def ensure_coverage_support():
    from testoob import coverage, testing
    if not coverage.supported():
        testing.skip(reason="No coverage support")
