"An alternative running scheme for unittest test suites"

__author__ = "Ori Peleg"

from main import *
from running import *
from extractors import *

###############################################################################
# examples
###############################################################################
def examples(suite):
    print "== filtered =="
    text_run(suite, test_extractor = regex_extractor("Th"))

    print "== sequential =="
    text_run(suite)

    print "== threaded =="
    try: text_run(suite, runner_class=ThreadedRunner)
    except Exception, e: print "Got error:", str(e)
