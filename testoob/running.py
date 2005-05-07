import unittest as _unittest

###############################################################################
# apply_runner
###############################################################################
# David Eppstein's breadth_first
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/231503
def _breadth_first(tree,children=iter):
    """Traverse the nodes of a tree in breadth-first order.
    The first argument should be the tree root; children
    should be a function taking as argument a tree node and
    returning an iterator of the node's children.
    """
    yield tree
    last = tree
    for node in _breadth_first(tree,children):
	for child in children(node):
	    yield child
	    last = child
	if last == node:
	    return

def extract_fixtures(suite, recursive_iterator=_breadth_first):
    """Extract the text fixtures from a suite.
    Descends recursively into sub-suites."""
    def test_children(node):
        if isinstance(node, _unittest.TestSuite): return iter(node)
        return []

    from itertools import ifilter
    return ifilter(lambda test: isinstance(test, _unittest.TestCase),
                   recursive_iterator(suite, children=test_children))

def apply_runner(suite, runner, test_extractor=extract_fixtures):
    """Runs the suite."""

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

class _TextTestResult(_unittest._TextTestResult):
    """provide defaults for unittest._TextTestResult"""
    def __init__(self, stream = None, descriptions=1, verbosity=1):
        if stream is None:
            import sys
            stream = sys.stderr
        stream = _unittest._WritelnDecorator(stream)
        _unittest._TextTestResult.__init__(self, stream, descriptions, verbosity)

def text_run(suite, runner_class=SimpleRunner, verbosity=1, **kwargs):
    """Run a suite and generate output similar to unittest.TextTestRunner's"""
    import sys
    class result_class(_unittest._TextTestResult):
        def __init__(self):
            _unittest._TextTestResult.__init__(self,
                         verbosity=verbosity,
                         descriptions=1,
                         stream=_unittest._WritelnDecorator(sys.stderr))
    import time
    start = time.time()
    result = apply_runner(suite, runner_class(result_class=result_class))
    timeTaken = time.time() - start
    
    _print_results(result, timeTaken)


