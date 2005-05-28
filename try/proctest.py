# preliminary tests in sending pickled objects to/from parents and children

import os, pickle, random, time, select, StringIO

def child(to_parent, from_parent):
    n = 0
    while n != 666:
        # TODO: this hanges, because this reads the entire stream at once.
        # This stream should be unpickled one-by-one.
        # Possible workarounds:
        # - send a sequence
        # - embed markers and read upto the marker
        # - maintain a StringIO=like object that can be read from _and_ written
        #   to
        n = pickle.loads(os.read(from_parent, 10000))

        d = {
            "pid" : os.getpid(),
            "n": n,
            "double" : n*2,
        }
        
        os.write(to_parent, pickle.dumps(d))

    print "[%d] done" % os.getpid()
    os.write(to_parent, pickle.dumps(666))
    os.close(from_parent)
    os.close(to_parent)
    raise SystemExit

def parent_read(fd, fds_left):
    d = pickle.loads(os.read(fd, 10000))
    if d == 666:
        fds_left.remove(fd)
    else:
        print os.getpid(), "[parent]", "[fd=%2d]"%fd, "[received %s]" % d

def spawn_child():
    from_child, to_parent = os.pipe()
    from_parent, to_child = os.pipe()
    if os.fork() == 0:
        child(to_parent, from_parent)
    else:
        return to_child, from_child

NUM_CHILDREN=3

def send_numbers(fds, val=None):
    for fd in fds:
        n = val or random.randint(1000,9999)
        print "[parent] sending %d" % n
        os.write(fd, pickle.dumps(n))

def perform_poll(poll, fds_left):
    for (fd, event) in poll.poll(1000):
        if event in (select.POLLHUP, select.POLLNVAL):
            fds_left.remove(fd)
            poll.unregister(fd)
        elif event in (select.POLLIN, select.POLLPRI):
            parent_read(fd, fds_left)
        else:
            print "Unexpected poll event '%s', fd=%d" % (event, fd)
            raise SystemExit

def send_input(children_to_fds):
    for i in xrange(3):
        send_numbers(children_to_fds)
    send_numbers(children_to_fds, 666)

def poll_output(children_from_fds):
    fds_left = children_from_fds[:]
    
    poll = select.poll()
    for fd in fds_left: poll.register(fd)

    while fds_left:
        perform_poll(poll, fds_left)

    print "fds_left:", fds_left

if __name__ == "__main__":
    children_from_fds = []
    children_to_fds = []

    for i in xrange(NUM_CHILDREN):
        to_child, from_child = spawn_child()
        children_from_fds.append(from_child)
        children_to_fds.append(to_child)

    send_input(children_to_fds)
    poll_output(children_from_fds)

    for fd in children_from_fds + children_to_fds: os.close(fd)
