import sys; sys.path.insert(0, "../src") # for testoob
import Pyro
import Pyro.core
import Pyro.naming

class NoMoreTests: pass # mark the end of the queue

fixture_ids = {}

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

		from Queue import Queue
		self.queue = Queue()

		self.pyro_queue = Pyro.core.ObjBase()
		self.pyro_queue.delegateTo(self.queue)

		self.daemon.connect(self.pyro_queue, ":testoob:test_queue")

		print "Server ready" # XXX

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

	while True:
		item = queue.get()
		if isinstance(item, NoMoreTests):
			return
		print "client:", item
	
	print "client: done"

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
