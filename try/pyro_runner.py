# vim:et:sw=4 ts=4
def fix_include_path():
    from sys import path
    from os.path import join, dirname
    path.insert(0, join(dirname(__file__), "..", "src"))
fix_include_path()
import os, sys

class PickleFriendlyReporterProxy:
    def __init__(self, reporter):
        self.reporter = reporter

    # direct proxies
    def addSuccess(self, test):
        self.reporter.addSuccess(test)
    def startTest(self, test):
        self.reporter.startTest(test)
    def stopTest(self, test):
        self.reporter.stopTest(test)

    # making tracebacks safe for pickling
    def addError(self, test, err):
        from testoob import reporting
        self.reporter.addError(test, reporting._exc_info_to_string(err, test))
    def addFailure(self, test, err):
        from testoob import reporting
        self.reporter.addFailure(test, reporting._exc_info_to_string(err, test))

    def addAssert(self, test, assertName, varList, err):
        raise NotImplementedError # TODO: check when we need this

class QueueIterator:
    """
    Iterate over a Queue.Queue instance until a sentinel is reached
    """
    def __init__(self, queue, **kwargs):
        """
        __init__(queue, [sentinel=SENTINEL], **kwargs)

        queue :
                the queue to iterate over
        sentinel : (optional keyword argument)
                the value signifying the end of the queue

        Other keyword arguments are passed to Queue.get
        """
        self.queue = queue
        self.has_sentinel = kwargs.has_key("sentinel")
        if self.has_sentinel:
            self.sentinel = kwargs["sentinel"]
            del kwargs["sentinel"]
        self.kwargs = kwargs
    def __iter__(self):
        return self
    def next(self):
        result = self.queue.get(**self.kwargs)
        if self.has_sentinel and result == self.sentinel:
            raise StopIteration
        return result

from testoob import running
class PyroRunner(running.BaseRunner):
    SLEEP_INTERVAL_BETWEEN_RETRYING_CONNECTION = 0.5
    GET_TIMEOUT = 20 # don't wait more than this for a test, on Python >= 2.3
    def __init__(self, num_processes):
        running.BaseRunner.__init__(self)
        from Queue import Queue
        self.queue = Queue()
        self.num_processes = num_processes
        self.fixture_ids = {}
        self._parent_pid = os.getpid()

    def _pyro_name(self, basename):
        "Return the name mangled for use in TestOOB's RPC"
        return ":testoob:%s:%s" % (basename, self._parent_pid)
    def _pyroloc_uri(self, basename):
        "Return the PYROLOC URI for the object, with proper mangling"
        return 'PYROLOC://localhost/%s' % self._pyro_name(basename)

    def _get_pyro_proxy(self, basename, timeout=40):
        "Safely try to get a proxy to the object, looping until timing out"
        import time, Pyro.core, Pyro.errors
        uri = self._pyroloc_uri(basename)
        starttime = time.time()
        while time.time() - starttime <= timeout:
            try:
                return Pyro.core.getProxyForURI(uri).getProxy()
            except Pyro.errors.ProtocolError:
                # object at the URI is unavailable, sleep a little
                time.sleep(PyroRunner.SLEEP_INTERVAL_BETWEEN_RETRYING_CONNECTION)
        raise RuntimeError("getting the proxy has timed out")

    def _get_id(self):
        try:
            self.current_id += 1
        except AttributeError:
            self.current_id = 0
        return "%s.%s" % (self._parent_pid, self.current_id)

    def run(self, fixture):
        self._register_fixture(fixture, self._get_id())

    def _register_fixture(self, fixture, id):
        assert id not in self.fixture_ids
        self.fixture_ids[id] = fixture
        self.queue.put(id)

    def _spawn_processes(self):
        # fork first child
        if os.fork() != 0: return # parent

        # fork the rest
        for i in xrange(1, self.num_processes):
            if os.fork() == 0: # child
                self._client_code()

        # run the client code on the first child too
        self._client_code()

    def done(self):
        for i in xrange(self.num_processes):
            self.queue.put(None)

        self._spawn_processes()

        self._server_code()

        running.BaseRunner.done(self)

    def _pyro_queue(self):
        import Pyro.core
        result = Pyro.core.ObjBase()
        result.delegateTo(self.queue)
        return result

    def _pyro_reporter(self):
        import Pyro.core
        result = Pyro.core.SynchronizedObjBase()
        result.delegateTo(self.reporter)
        return result

    def _server_code(self):
        "The Pyro server code, runs in the parent"
        import Pyro.core
        Pyro.core.initServer(banner=False)

        daemon = Pyro.core.Daemon()
        
        daemon.connect(self._pyro_queue(), self._pyro_name("queue"))
        daemon.connect(self._pyro_reporter(), self._pyro_name("reporter"))

        # == running
        daemon.requestLoop(condition=lambda:not self.queue.empty())

        # == cleanup
        daemon.shutdown()

    def _run_fixtures(self):
        queue = self._get_pyro_proxy("queue")
        remote_reporter = self._get_pyro_proxy("reporter")
        local_reporter = PickleFriendlyReporterProxy(remote_reporter)

        for id in QueueIterator(queue,
                                sentinel=None,
                                timeout=PyroRunner.GET_TIMEOUT):
            fixture = self.fixture_ids[id]
            fixture(local_reporter)

    def _client_code(self):
        "The Pyro client code, runs in the child"
        import Pyro.errors, Pyro.core

        Pyro.core.initClient(banner=False)

        import sys
        try:
            self._run_fixtures()

        except Pyro.errors.ConnectionClosedError:
            # report the error gracefully
            print >>sys.stderr, "[TestOOB+Pyro pid=%d] " \
                  "child lost connection to parent, exiting" % os.getpid()
            sys.exit(1)

        sys.exit(0) # everything was successful

def main(num_processes=1):
    print "num_processes=%s" % num_processes
    import suite, sys
    from testoob import reporting, extracting

    running.run_suites(
            suites=[suite.suite()],
            reporters=[reporting.TextStreamReporter(sys.stderr, 0, 0)],
            runner=PyroRunner(num_processes),
        )

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(int(sys.argv[1]))
    else:
        main()
