# preliminary tests in sending pickled objects to/from parents and children

import os, pickle, random

def child(to_parent, from_parent):
    n = pickle.loads(os.read(from_parent, 10000))
    os.close(from_parent)

    d = {
        "pid" : os.getpid(),
        "n": n,
        "double" : n*2,
    }
    
    os.write(to_parent, pickle.dumps(d))
    os.close(to_parent)
    raise SystemExit

def parent_read(fd):
    d = pickle.loads(os.read(fd, 10000))
    os.close(fd)
    print os.getpid(), "[parent]", "[fd=%2d]"%fd, "[received %s]" % d

def spawn_child():
    from_child, to_parent = os.pipe()
    from_parent, to_child = os.pipe()
    if os.fork() == 0:
        child(to_parent, from_parent)
    else:
        return to_child, from_child

NUM_CHILDREN=10

if __name__ == "__main__":
    children_from_fds = []
    for i in xrange(NUM_CHILDREN):
        to_child, from_child = spawn_child()
        n = random.randint(1000,9999)
        print "[parent] sending %d" % n
        os.write(to_child, pickle.dumps(n))
        os.close(to_child)
        children_from_fds.append(from_child)
    
    import select
    poll = select.poll()
    for fd in children_from_fds: poll.register(fd)
    while children_from_fds:
        for (fd, event) in poll.poll():
            if event in (select.POLLHUP, select.POLLNVAL):
                children_from_fds.remove(fd)
            elif event in (select.POLLIN, select.POLLPRI):
                parent_read(fd)
            else:
                print "Unexpected poll event '%s', fd=%d" % (event, fd)
                raise SystemExit

