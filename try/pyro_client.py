import sys; sys.path.insert(0, "../src") # for testoob
import time
import Pyro
import Pyro.core
import Pyro.naming
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
