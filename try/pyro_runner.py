# vim:et:sw=4 ts=4
import sys; sys.path.insert(0, "../src") # for testoob
import Pyro
import Pyro.core
import os
import time

parent_pid = os.getpid()
SLEEP_INTERVAL_BETWEEN_RETRYING_CONNECTION = 0.5

def pyro_name(basename):
    return ":testoob:%s:%s" % (basename, parent_pid)

class NoMoreTests: pass # mark the end of the queue

fixture_ids = {}

from testoob import running
class PyroRunner(running.BaseRunner):
    def __init__(self, num_processes):
        running.BaseRunner.__init__(self)
        from Queue import Queue
        self.queue = Queue()
        self.num_processes = num_processes

    def _get_id(self):
        try:
            self.current_id += 1
        except AttributeError:
            self.current_id = 0
        return self.current_id

    def run(self, fixture):
        id = self._get_id()
        fixture_ids[id] = fixture
        self.queue.put(id) # register fixture id

    def _spawn_processes(self):
        for i in xrange(self.num_processes):
            if os.fork() == 0:
                # child
                client_code()
                sys.exit(0)

    def done(self):
        for i in xrange(self.num_processes):
            self.queue.put(NoMoreTests())

        self._spawn_processes()

        server_code(self.queue, self.reporter)

        running.BaseRunner.done(self)

def server_code(queue, reporter):
    Pyro.core.initServer()

    daemon = Pyro.core.Daemon()

    pyro_queue = Pyro.core.ObjBase()
    pyro_queue.delegateTo(queue)

    pyro_reporter = Pyro.core.SynchronizedObjBase()
    pyro_reporter.delegateTo(reporter)

    daemon.connect(pyro_queue, ":testoob:queue")
    daemon.connect(pyro_reporter, ":testoob:reporter")

    # == running
    daemon.requestLoop(condition=lambda:not queue.empty())

    # == cleanup
    daemon.shutdown()

def client_code():
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
    reporter = safe_get_proxy('PYROLOC://localhost/:testoob:reporter')

    try:
        while True:
            id = queue.get()
            if isinstance(id, NoMoreTests):
                break
            fixture = fixture_ids[id]
            fixture(reporter)
    except Pyro.errors.ConnectionClosedError:
        print >>sys.stderr, "[%d] connection to server lost, exiting" % os.getpid()
        sys.exit(1)

def main(num_processes=1):
    print "num_processes=%s" % num_processes
    import suite, sys
    from testoob import reporting

    suite = suite.suite()
    reporter = reporting.TextStreamReporter(sys.stderr, 0, 0)
    runner = PyroRunner(num_processes)

    running.run_suites(suites=[suite], reporters=[reporter], runner=runner)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(int(sys.argv[1]))
    else:
        main()
