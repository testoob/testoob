# vim:et:sw=4 ts=4
import sys; sys.path.insert(0, "../src") # for testoob
import Pyro
import Pyro.core
import os

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
        print "Registering id %02d ==> %r" % (id, fixture) # XXX
        fixture_ids[id] = fixture
        self.queue.put(id) # register fixture id

    def _spawn_processes(self):
        print "spawning %d processes:" % self.num_processes, # XXX
        for i in xrange(self.num_processes):
            print i,; sys.stdout.flush() # XXX
            if os.fork() == 0:
                # child
                client_code()
                sys.exit(0)

    def done(self):
        for i in xrange(self.num_processes):
            self.queue.put(NoMoreTests())

        self._spawn_processes()

        server_code(self.queue, self.reporter)

        print "PyroRunner: done" # XXX
        running.BaseRunner.done(self)

def server_code(queue, reporter):
    print "server: started" # XXX
    Pyro.core.initServer()

    daemon = Pyro.core.Daemon()

    pyro_queue = Pyro.core.ObjBase()
    pyro_queue.delegateTo(queue)

    pyro_reporter = Pyro.core.SynchronizedObjBase()
    pyro_reporter.delegateTo(reporter)

    daemon.connect(pyro_queue, ":testoob:queue")
    daemon.connect(pyro_reporter, ":testoob:reporter")

    print "server: ready" # XXX

    # == running
    daemon.requestLoop(condition=lambda:not queue.empty())

    # == cleanup

    print "server: cleaning up" # XXX
    daemon.shutdown() # TODO

def client_code():
    print "client: started" # XXX
    import time
    time.sleep(3)
    import Pyro.errors
    Pyro.core.initClient()

    queue = Pyro.core.getProxyForURI('PYROLOC://localhost/:testoob:queue').getProxy()
    reporter = Pyro.core.getProxyForURI('PYROLOC://localhost/:testoob:reporter').getProxy()

    while True:
        id = queue.get()
        if isinstance(id, NoMoreTests):
            break
        print "client: id=%s" % id
        fixture = fixture_ids[id]
        fixture(reporter)

    print "client: done"

def main():
    import suite, sys
    from testoob import reporting

    suite = suite.suite()
    reporter = reporting.TextStreamReporter(sys.stdout, 0, 0)

    running.run_suites(suites=[suite], reporters=[reporter], runner=PyroRunner(4))

if __name__ == "__main__":
    main()
