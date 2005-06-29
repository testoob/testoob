"Extracting tests from a test suite"
from __future__ import generators # Python 2.2 compatibility

try:
    from itertools import ifilter as _ifilter
except ImportError:
    from compatibility.itertools import ifilter as _ifilter

# David Eppstein's breadth_first
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/231503
def _breadth_first(tree,children=iter):
    """Traverse the nodes of a tree in breadth-first order.
    The first argument should be the tree root; children
    should be a function taking as argument a tree node and
    returning an iterator of the node's children.
    """
    yield tree
    last = tree
    for node in _breadth_first(tree,children):
	for child in children(node):
	    yield child
	    last = child
	if last == node:
	    return

def suite_iter(suite):
    """suite_iter(suite) -> an iterator on its direct sub-suites.
    For compatibility with Python versions before 2.4"""
    try:
        return iter(suite)
    except TypeError:
        return iter(suite._tests) # Before 2.4, test suites weren't iterable

def extract_fixtures(suite, recursive_iterator=_breadth_first):
    """Extract the text fixtures from a suite.
    Descends recursively into sub-suites."""
    import unittest
    def test_children(node):
        if isinstance(node, unittest.TestSuite): return suite_iter(node)
        return []

    return _ifilter(lambda test: isinstance(test, unittest.TestCase),
                    recursive_iterator(suite, children=test_children))

def regex_extractor(regex):
    """Filter tests based on matching a regex to their id.
    Matching is performed with re.search"""
    import re
    compiled = re.compile(regex)
    def pred(test): return compiled.search(test.id())
    def wrapper(suite):
        return _ifilter(pred, extract_fixtures(suite))
    return wrapper

