# vim:et:sw=4 ts=4
def fix_include_path():
    from sys import path
    from os.path import join, dirname
    path.insert(0, join(dirname(__file__), "..", "src"))
fix_include_path()
import Pyro
import Pyro.core
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
        Pyro.core.initServer()

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
        def safe_get_proxy(uri, timeout=40):
            starttime = time.time()
            while time.time() - starttime <= timeout:
                try:
                    return Pyro.core.getProxyForURI(uri).getProxy()
                except Pyro.errors.ProtocolError:
                    time.sleep(SLEEP_INTERVAL_BETWEEN_RETRYING_CONNECTION)
            raise RuntimeError("safe_get_proxy has timed out")

        import Pyro.errors
        Pyro.core.initClient()

        queue = safe_get_proxy('PYROLOC://localhost/:testoob:queue')
        remote_reporter = safe_get_proxy('PYROLOC://localhost/:testoob:reporter')

        class PickleFriendlyReporterProxy:
            def __init__(self, reporter):
                self.reporter = reporter
            def addSuccess(self, test):
                self.reporter.addSuccess(str(test)) # converting test to string
            def addError(self, test, err):
                self.reporter.addError(str(test), str(err))
            def addFailure(self, test, err):
                self.reporter.addFailure(str(test), str(err))

        try:
            while True:
                id = queue.get()
                if isinstance(id, NoMoreTests):
                    break
                print "client:", id # XXX
                fixture = self.fixture_ids[id]
                fixture(remote_reporter)
        except Pyro.errors.ConnectionClosedError:
            # report the error gracefully
            print >>sys.stderr, "[%d] connection to server lost, exiting" % os.getpid()
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
            extraction_decorators=[extracting.regex("WillFail")],
        )

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(int(sys.argv[1]))
    else:
        main()
