# TestOOB, Python Testing Out Of (The) Box
# Copyright (C) 2005 The TestOOB Team
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

"Some useful test-collecting functions"

from __future__ import generators

try:
    from itertools import ifilter as _ifilter
except ImportError:
    from compatibility.itertools import ifilter as _ifilter

def _is_test_case(x):
    import types, unittest
    try:
        return issubclass(x, unittest.TestCase)
    except TypeError:
        # x isn't a class
        return False

def collect(globals_dict):
    import warnings
    warnings.warn(
        "'collect' has been renamed to 'collector_from_globals'",
        category=DeprecationWarning
    )
    return collector_from_globals(globals_dict)
def collector_from_globals(globals_dict):
    """
    Returns a function that collects all TestCases from the given globals
    dictionary, and registers them in a new TestSuite, returning it.
    """
    import unittest
    def suite():
        result = unittest.TestSuite()
        for test_case in _ifilter(_is_test_case, globals_dict.values()):
            result.addTest(unittest.makeSuite(test_case))
        return result
    return suite

def collect_from_modules(modules, globals_dict):
    import warnings
    warnings.warn(
        "'collect_from_modules' has been renamed to 'collector_from_modules'",
        category=DeprecationWarning
    )
    return collector_from_modules(modules, globals_dict)
def collector_from_modules(modules, globals_dict):
    """
    Returns a function that collects all TestCases from the given module name
    list, and the given globals dictionary, and registers them in a new
    TestSuite, returning it.
    """
    import unittest
    def suite():
        result = unittest.TestSuite()
        for modulename in modules:
            NONEMPTYLIST = [None] # help(__import__) says we need this.
            result.addTest(
                __import__(modulename, globals_dict, None, NONEMPTYLIST).suite()
            )
        return result
    return suite
