"unit tests for testoob.running"

import unittest
import testoob.running
import mock

class test_BaseRunner(unittest.TestCase):
    def setUp(self):
        self.runner = testoob.running.BaseRunner()
        self.runner.reporter = mock.Mock()

    def test_done(self):
        self.runner.reporter.mockAddReturnValues(done=False)
        self.runner.done()
        self.assertEqual(1, len(self.runner.reporter.mockGetNamedCalls("done")))

    def test_isSuccesful_true(self):
        self.runner.reporter.mockAddReturnValues(isSuccessful=True)
        self.assertEqual(True, self.runner.isSuccessful())

    def test_isSuccesful_false(self):
        self.runner.reporter.mockAddReturnValues(isSuccessful=False)
        self.assertEqual(False, self.runner.isSuccessful())

class test_SimpleRunner(unittest.TestCase):
    def setUp(self):
        self.runner = testoob.running.SimpleRunner()
        self.runner.reporter = mock.Mock()

    def test_run_retval_true(self):
        self.runner.reporter.mockAddReturnValues( isSuccessful=True )
        self.assertEqual(True, self.runner.run(fixture = mock.Mock()))

    def test_run_retval_false(self):
        self.runner.reporter.mockAddReturnValues( isSuccessful=False )
        self.assertEqual(False, self.runner.run(fixture = mock.Mock()))

    def test_run(self):
        fixture = mock.Mock()
        self.runner.run(fixture)
        self.assertEqual(1, len(fixture.mockGetNamedCalls("__call__")))

if __name__ == "__main__":
    import testoob
    testoob.main()
