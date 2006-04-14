"Dummy project to write tests for"

def do_things(cond):
    if cond:
        return 4
    else:
        return 5

def do_more_things():
    x = 1
    for i in xrange(10):
        x *= 2
    if x%3 == 15:
        return 5
    return 6
