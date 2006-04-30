#! /usr/bin/env python
def script_dir():
    from os.path import abspath, normpath, dirname
    return normpath(abspath(dirname(__file__)))

def blat_executable():
    from os.path import join
    return join(script_dir(), "blat.py")

def main():
    import sys, os
    if len(sys.argv) == 1:
        print "Usage: %s host1 [host2 [host3 ...]]" % os.path.basename(sys.argv[0])
        sys.exit(1)
    executable = blat_executable() # put in local vars dict
    for host in sys.argv[1:]:
        print "host:", host
        os.system("ssh %(host)s %(executable)s >& %(host)s.report" % vars())

if __name__ == "__main__":
    main()
