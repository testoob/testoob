# Testoob, Python Testing Out Of (The) Box
# Copyright (C) 2005-2006 The Testoob Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

    def add_extra_description_field(test):
        test._testoob_extra_description = ""
        return True

    try:
        return _ifilter(add_extra_description_field, iter(suite))
    except TypeError:
        # Before 2.4, test suites weren't iterable
        return _ifilter(add_extra_description_field, iter(suite._tests))

def full_extractor(suite, recursive_iterator=_breadth_first):
    """Extract the text fixtures from a suite.
    Descends recursively into sub-suites."""
    import unittest
    def test_children(node):
        if isinstance(node, unittest.TestSuite): return suite_iter(node)
        return []

    return _ifilter(lambda test: isinstance(test, unittest.TestCase),
                    recursive_iterator(suite, children=test_children))

def _iterable_decorator(func):
    def decorator(extractor):
        def wrapper(*args, **kwargs):
            return func(extractor(*args, **kwargs))
        return wrapper
    return decorator

def predicate(pred):
    return _iterable_decorator(lambda iterable: _ifilter(pred, iterable))

def regex(regex):
    """Filter tests based on matching a regex to their id.
    Matching is performed with re.search"""
    import re
    compiled = re.compile(regex)
    def pred(test):return compiled.search(test.id())
    return predicate(pred)

def glob(pattern):
    """Filter tests based on a matching glob pattern to their id.
    Matching is performed with fnmatch.fnmatchcase"""
    import fnmatch
    def pred(test): return fnmatch.fnmatchcase(test.id(), pattern)
    return predicate(pred)

number_suffixes = {1: "st",
                   2: "nd",
                   3: "ed",
                  }
def _irepeat_items(num_times, iterable):
    for x in iterable:
        for i in xrange(num_times):
            x._testoob_extra_description = " (%d%s iteration)" % (i + 1, number_suffixes.get(i + 1, "th"))
            yield x

def repeat(num_times):
    "Repeat each test a number of times"
    return _iterable_decorator(lambda iterable: _irepeat_items(num_times, iterable))

def _irandomize(iterable, seed=None):
    """
    Randomize the iterable.

    Note: this evaluates the entire iterable to a sequence in memory, use
    this when this isn't an issue
    """
    if seed is None:
        from random import shuffle
    else:
        from random import Random
        shuffle = Random(seed).shuffle
    result = list(iterable)
    shuffle(result)
    return iter(result)

def randomize(seed=None):
    "Randomize the order of the tests"
    return _iterable_decorator(lambda iterable: _irandomize(iterable, seed))

