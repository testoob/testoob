# vim:et:sw=4 ts=4
def fix_include_path():
    from sys import path
    from os.path import join, dirname
    path.insert(0, join(dirname(__file__), "..", "src"))
fix_include_path()
import time, os, sys

parent_pid = os.getpid()
SLEEP_INTERVAL_BETWEEN_RETRYING_CONNECTION = 0.5

def pyro_name(basename):
    return ":testoob:%s:%s" % (basename, parent_pid)

class NoMoreTests: pass # mark the end of the queue

from testoob import running
class PyroRunner(running.BaseRunner):
    def __init__(self, num_processes):
        running.BaseRunner.__init__(self)
        from Queue import Queue
        self.queue = Queue()
        self.num_processes = num_processes
        self.fixture_ids = {}

    def _get_id(self):
        try:
            self.current_id += 1
        except AttributeError:
            self.current_id = 0
        return "%s.%s" % (parent_pid, self.current_id)

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
            self.queue.put(NoMoreTests())

        self._spawn_processes()

        self._server_code()

        running.BaseRunner.done(self)

    def _server_code(self):
        import Pyro.core
        Pyro.core.initServer(banner=0)

        daemon = Pyro.core.Daemon()

        pyro_queue = Pyro.core.ObjBase()
        pyro_queue.delegateTo(self.queue)

        pyro_reporter = Pyro.core.SynchronizedObjBase()
        pyro_reporter.delegateTo(self.reporter)

        daemon.connect(pyro_queue, ":testoob:queue")
        daemon.connect(pyro_reporter, ":testoob:reporter")

        # == running
        daemon.requestLoop(condition=lambda:not self.queue.empty())

        # == cleanup
        daemon.shutdown()

    def _client_code(self):
        import Pyro.errors, Pyro.core
        def safe_get_proxy(uri, timeout=40):
            starttime = time.time()
            while time.time() - starttime <= timeout:
                try:
                    return Pyro.core.getProxyForURI(uri).getProxy()
                except Pyro.errors.ProtocolError:
                    time.sleep(SLEEP_INTERVAL_BETWEEN_RETRYING_CONNECTION)
            raise RuntimeError("safe_get_proxy has timed out")

        Pyro.core.initClient(banner=0)

        queue = safe_get_proxy('PYROLOC://localhost/:testoob:queue')
        remote_reporter = safe_get_proxy('PYROLOC://localhost/:testoob:reporter')

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

            #def addAssert(self, test, assertName, varList, err):
            #    "Called when an assert was made (if err is None, the assert passed)"
            #    pass

        local_reporter = PickleFriendlyReporterProxy(remote_reporter)

        try:
            while True:
                id = queue.get()
                if isinstance(id, NoMoreTests):
                    break
                fixture = self.fixture_ids[id]
                fixture(local_reporter)
        except Pyro.errors.ConnectionClosedError:
            # report the error gracefully
            print >>sys.stderr, "[TestOOB+Pyro pid=%d] child lost connection to parent, exiting" % os.getpid()
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
