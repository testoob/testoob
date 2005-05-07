# Fix path to use development version
import sys, os
sys.path.insert(0, os.path.join(os.path.basename(sys.argv[0]), ".."))

import testoob

from regular_suite import CaseDigits, CaseLetters

def helper_main_with_args(*args):
    old_argv = sys.argv
    import copy
    sys.argv = copy.copy(old_argv)
    sys.argv.extend(args)

    test_main_noargs()

    sys.argv = old_argv

def suite():
    import regular_suite
    return regular_suite.suite()

def test_main_noargs():
    testoob.main()

def test_main_verbose():
    helper_main_with_args("-v")

def test_main_quiet():
    helper_main_with_args("-q")

def test_main_regex():
    helper_main_with_args("--regex=1|B")

def test_main_suite():
    import regular_suite
    testoob.main(suite=regular_suite.suite())

def test_main_defaultTest():
    testoob.main(defaultTest="suite")

if __name__ == "__main__":
    for name, value in globals().items():
        if name.startswith("test_") and callable(value):
            print >>sys.stderr, "*", name
            value()
