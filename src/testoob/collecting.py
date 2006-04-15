# Testoob, Python Testing Out Of (The) Box
# Copyright (C) 2005 The Testoob Team
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

def _first_external_frame():
    import sys

    current_file = sys._getframe().f_code.co_filename

    # find the first frame with a filename different than this one
    frame = sys._getframe()
    while frame.f_code.co_filename == current_file:
        frame = frame.f_back

    return frame

def _calling_module_name():
    return _first_external_frame().f_globals["__name__"]

def _calling_module_directory():
    from os.path import dirname, normpath
    return normpath(dirname(_first_external_frame().f_code.co_filename))

def _module_names(glob_pattern, modulename, path):
    import glob
    from os.path import splitext, basename, join
    return [
        modulename + "." + splitext(basename(filename))[0]
        for filename in glob.glob( join(path, glob_pattern) )
    ]

def _load_suite(module_name):
    import unittest
    result = unittest.TestLoader().loadTestsFromName( module_name )
    if len(result._tests) == 0:
        import warnings
        warnings.warn("No tests loaded for module '%s'" % module_name)
    return result

def collect_from_files(glob_pattern, modulename=None, path=None):
    if modulename is None:
        modulename = _calling_module_name()

    if path is None:
        path = _calling_module_directory()

    # mimicking unittest.TestLoader.loadTestsFromNames, but with more checks
    suites = [
        _load_suite(name)
        for name in _module_names(glob_pattern, modulename, path)
    ]

    import unittest
    return unittest.TestLoader().suiteClass(suites)
