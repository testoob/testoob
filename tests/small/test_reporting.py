from unittest import TestCase

class MethodsCalledMock:
    def __init__(self):
        self.last_method = None
        self.last_args = None
        self.last_kwargs = None
    def __getattr__(self, name):
        def record_run(*args, **kwargs):
            self.last_method = name
            self.last_args = args
            self.last_kwargs = kwargs
        return record_run

class reporter_proxy_proxies(TestCase):
    def setUp(self):
        from testoob.reporting.reporter_proxy import ReporterProxy
        self.proxy = ReporterProxy()
        self.reporter = MethodsCalledMock()
        self.proxy.add_observer(self.reporter)

    def tearDown(self):
        del self.proxy
        del self.reporter

    def _check_method_proxy(self, method_name, *args):
        method = getattr(self.proxy, method_name)
        method(*args)
        self.assertEqual( method_name, self.reporter.last_method )

    def test_start(self):
        self._check_method_proxy("start")
    def test_done(self):
        self._check_method_proxy("done")
    def test_startTest(self):
        self._check_method_proxy("startTest", None)
    def test_stopTest(self):
        self._check_method_proxy("stopTest", None)
    def test_addError(self):
        self._check_method_proxy("addError", None, None)
    def test_addFailure(self):
        self._check_method_proxy("addFailure", None, None)
    def test_addSuccess(self):
        self._check_method_proxy("addSuccess", None)
    def test_addAssert(self):
        self._check_method_proxy("addAssert", None, None, None, None)
    def test_isSuccessful(self):
        self._check_method_proxy("isSuccessful")

class reporter_proxy_isSuccessful(TestCase):
    def setUp(self):
        from testoob.reporting.reporter_proxy import ReporterProxy
        self.proxy = ReporterProxy()

        from testoob.reporting.base import BaseReporter
        class SuccessReporter(BaseReporter):
            def __init__(self):
                BaseReporter.__init__(self)
                self.success = True
            def isSuccessful(self):
                return self.success

        self.reporters = (SuccessReporter(), SuccessReporter())
        for reporter in self.reporters:
            self.proxy.add_observer(reporter)

    def tearDown(self):
        del self.reporters
        del self.proxy

    def test_all_success(self):
        self.failUnless( self.proxy.isSuccessful() )

    def test_one_failure(self):
        self.reporters[0].success = False
        self.failIf( self.proxy.isSuccessful() )

    def test_all_failures(self):
        for reporter in self.reporters:
            reporter.success = False
        self.failIf( self.proxy.isSuccessful() )

if __name__ == "__main__":
    import testoob
    testoob.main()
