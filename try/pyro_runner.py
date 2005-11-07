# vim:et:sw=4 ts=4
import sys; sys.path.insert(0, "../src") # for testoob
import Pyro
import Pyro.core
import os

class NoMoreTests: pass # mark the end of the queue

fixture_ids = {}

def create_pyro_server(queue):
    Pyro.core.initServer()

    daemon = Pyro.core.Daemon()

    pyro_queue = Pyro.core.ObjBase()
    pyro_queue.delegateTo(queue)

    daemon.connect(pyro_queue, ":testoob:test_queue")

    print "Server ready" # XXX

    # == running
    print "Waiting for client" # XXX
    daemon.requestLoop(condition=lambda:not queue.empty())

    # == cleanup

    print "Cleaning up" # XXX
    daemon.shutdown() # TODO

from testoob import running
class PyroRunner(running.BaseRunner):
    def __init__(self):
        running.BaseRunner.__init__(self)
        from Queue import Queue
        self.queue = Queue()

    def _get_id(self):
        try:
            self.current_id += 1
        except AttributeError:
            self.current_id = 0
        return self.current_id

    def run(self, fixture):
        id = self._get_id()
        print "Registering id %02d ==> %r" % (id, fixture) # XXX
        fixture_ids[id] = fixture
        self.queue.put(id) # register fixture id

    def done(self):
        self.queue.put(NoMoreTests())

        if os.fork() == 0:
            # child
            client_code()
        else:
            # parent
            create_pyro_server(self.queue)

        print "All done :-)" # XXX
        running.BaseRunner.done(self)

def client_code():
    print "client started" # XXX
    import time
    time.sleep(3)
    import Pyro.errors
    Pyro.core.initClient()

    def get_uri():
        while True:
            try:
                return Pyro.core.getProxyForURI('PYROLOC://localhost/:testoob:test_queue')
            except Pyro.errors.NamingError:
                time.sleep(0.2)

    print "client: waiting for queue registration"
    uri = get_uri()
    print "client: queue has been registered"

    queue = uri.getProxy()

    from testoob import reporting
    reporter = reporting.TextStreamReporter(sys.stdout, 0, 1)

    while True:
        id = queue.get()
        if isinstance(id, NoMoreTests):
            break
        print "client: id=%s" % id
        fixture = fixture_ids[id]
        fixture(reporter)

    print "client: done"

def main():
    print "server started" # XXX
    import suite, sys
    from testoob import reporting

    suite = suite.suite()
    reporter = reporting.TextStreamReporter(sys.stdout, 0, 0)

    running.run_suites(suites=[suite], reporters=[reporter], runner=PyroRunner())

if __name__ == "__main__":
    main()
