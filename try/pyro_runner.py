import sys; sys.path.insert(0, "../src") # for testoob
import Pyro
import Pyro.core
import Pyro.naming


fixture_dict = {}

class StrQueue:
	def __init__(self):
		self._queue = []
		self._ready = False
		self._done = False
	def push(self, obj): self._queue.append(obj)
	def pop(self):return str(self._queue.pop())
	def empty(self): return len(self._queue) == 0
	def ready(self): return self._ready
	def mark_ready(self): self._ready = True
	def done(self): return self._done
	def mark_done(self): self._done = True

from testoob import running
class PyroRunner(running.BaseRunner):
	def __init__(self):
		running.BaseRunner.__init__(self)

		Pyro.core.initServer()

		# TODO: create our own nameserver in another process, see pyro-ns's
		#       code
		#    -OR-
		#       don't use a nameserver, publish the server on a specific port
		#       and have the clients connect to it
		locator = Pyro.naming.NameServerLocator()
		ns = locator.getNS()

		self.daemon = Pyro.core.Daemon()
		self.daemon.useNameServer(ns)

		self.queue = StrQueue()

		self.pyro_queue = Pyro.core.SynchronizedObjBase()
		self.pyro_queue.delegateTo(self.queue)

		self.daemon.connect(self.pyro_queue, ":testoob:test_queue")

		print "Server ready" # XXX


	def run(self, fixture):
		print "Registering %r" % fixture # XXX
		self.queue.push(fixture) # register fixture
		self.queue.mark_ready()

	def done(self):
		self.queue.mark_done()

		# == running
		# TODO: run in run()? This way tests can run during the setup
		print "Waiting for client" # XXX
		self.daemon.requestLoop(condition=lambda:not self.queue.empty())

		# == cleanup

		print "Cleaning up" # XXX
		self.daemon.shutdown() # TODO ???

		print "All done :-)" # XXX
		running.BaseRunner.done(self)

def client_code():
	print "client started" # XXX
	import time
	time.sleep(3)
	import Pyro.errors
	Pyro.core.initClient()


	locator = Pyro.naming.NameServerLocator()
	ns = locator.getNS()

	def get_uri():
		while True:
			try:
				return ns.resolve(":testoob:test_queue")
			except Pyro.errors.NamingError:
				time.sleep(1)

	print "client: waiting for queue registration"
	uri = get_uri()
	print "client: queue has been registered"

	queue = uri.getProxy()

	#from testoob import reporting
	#reporter = reporting.TextStreamReporter(sys.stdout)

	def wait_for_queue():
		print "client: waiting for queue readiness"
		while not queue.ready():
			time.sleep(0.1)
		print "client: queue is ready"
	wait_for_queue()

	while not queue.empty() and queue.done():
		print "client:", queue.pop()

def server_code():
	print "server started" # XXX
	import suite, sys
	from testoob import reporting

	suite = suite.suite()
	reporter = reporting.TextStreamReporter(sys.stdout, 0, 0)

	running.run_suites(suites=[suite], reporters=[reporter], runner=PyroRunner())

if __name__ == "__main__":
	import os
	if os.fork() == 0:
		# child
		client_code()
	else:
		server_code()
