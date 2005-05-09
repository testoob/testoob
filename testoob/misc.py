"Code that isn't currently filed or"

# Connelly Barnes's (connellybarnes at yahoo.com) threadclass
# http://mail.python.org/pipermail/python-list/2004-June/225478.html
import types as _types
def _threadclass(C):
  """Returns a 'threadsafe' copy of class C.
     All public methods are modified to lock the
     object when called."""

  class D(C):
    def __init__(self, *args, **kwargs):
      import threading
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
    if isinstance(f, _types.UnboundMethodType) and a[:2] != '__':
      setattr(D, a, ubthreadfunction(f))
  return D

from running import SimpleRunner as _SimpleRunner
class ThreadedRunner(_SimpleRunner):
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

