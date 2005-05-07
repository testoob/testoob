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

    return runner.result()

###############################################################################
# Runners
###############################################################################

class SimpleRunner:
    def __init__(self, result_class=None, result=None):
        if result is not None:         self._result = result
        elif result_class is not None: self._result = result_class()
        else:
            raise TypeError("neither result or result_class given")
        self._done = False

    def run(self, fixture):
        assert not self._done
        fixture(self._result)

    def result(self):
        self._done = True
        return self._result

# Connelly Barnes's (connellybarnes at yahoo.com) threadclass
# http://mail.python.org/pipermail/python-list/2004-June/225478.html
import types, threading
def _threadclass(C):
  """Returns a 'threadsafe' copy of class C.
     All public methods are modified to lock the
     object when called."""

  class D(C):
    def __init__(self, *args, **kwargs):
      self.lock = threading.RLock()
      C.__init__(self, *args, **kwargs)

  def ubthreadfunction(f):
    def g(self, *args, **kwargs):
      self.lock.acquire()
      try:
          return f(self, *args, **kwargs)
      finally:
          self.lock.release()
    return g

  for a in dir(D):
    f = getattr(D, a)
    if isinstance(f, types.UnboundMethodType) and a[:2] != '__':
      setattr(D, a, ubthreadfunction(f))
  return D

class ThreadedRunner(SimpleRunner):
    """Run tests using a threadpool.
    Uses TwistedPython's thread pool"""
    def __init__(self, result_class):
        from twisted.python.threadpool import ThreadPool

        SimpleRunner.__init__(self, _threadclass(result_class))
        
        self._pool = ThreadPool()
        self._pool.start()

    def run(self, fixture):
        assert not self._done
        self._pool.dispatch(None, fixture, self._result)

    def result(self):
        self._pool.stop()
        return SimpleRunner.result(self)

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
    class result_class(_unittest._TextTestResult):
        def __init__(self):
            _unittest._TextTestResult.__init__(self,
                         verbosity=verbosity,
                         descriptions=1,
                         stream=_unittest._WritelnDecorator(sys.stderr))

    import time
    runner = runner_class(result_class=result_class)

    start = time.time()
    result = apply_runner(suites=suites,
                          runner=runner,
                          test_extractor=test_extractor)
    timeTaken = time.time() - start
    
    _print_results(result, timeTaken)


