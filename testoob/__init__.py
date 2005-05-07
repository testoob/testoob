"An alternative running scheme for unittest test suites"

__author__ = "Ori Peleg"

from itertools import ifilter as _ifilter

# main() function
from main import *
from running import *

###############################################################################
# Test extractors
###############################################################################
def regexp_extractor(regexp):
    """Filter tests based on matching a regexp to their id.
    Matching is performed with re.search"""
    import re
    compiled = re.compile(regexp)
    def pred(test): return compiled.search(test.id())
    def wrapper(suite):
        return _ifilter(pred, extract_fixtures(suite))
    return wrapper

###############################################################################
# examples
###############################################################################
def examples(suite):
    print "== sequential =="
    text_run(suite)

    print "== threaded =="
    text_run(suite, ThreadedRunner)

    print "== filtered =="
    text_run(suite, test_extractor = regexp_extractor("Th"))
