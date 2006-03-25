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

"Special test loaders"

import unittest

class CustomMethodNameLoader(unittest.TestLoader):
    "Load test methods based on a predicate"
    def __init__(self, *args, **kwargs):
        # in Python 2.2, unittest.TestLoader gets no default __init__, so we
        # wrap it here
        if hasattr(unittest.TestLoader, "__init__"):
            unittest.TestLoader.__init__(self, *args, **kwargs)

    def getTestCaseNames(self, testCaseClass):
        "Return the method names matching the predicate"
        # code from unittest.TestLoader.getTestCaseNames, but with a predicate
        # hook
        def isTestMethod(name):
            if not self._testNamePredicate(name): return False
            if not callable(getattr(testCaseClass, name)): return False
            return True
        testFnNames = filter(isTestMethod, dir(testCaseClass))
        for baseclass in testCaseClass.__bases__:
            for testFnName in self.getTestCaseNames(baseclass):
                if testFnName not in testFnNames:  # handle overridden methods
                    testFnNames.append(testFnName)
        if self.sortTestMethodsUsing:
            testFnNames.sort(self.sortTestMethodsUsing)
        return testFnNames

class RegexLoader(CustomMethodNameLoader):
    "Load test methods matching the regular expression"
    def __init__(self, regex):
        CustomMethodNameLoader.__init__(self)
        import re
        self.pattern = re.compile(regex)

    def _testNamePredicate(self, name):
        return self.pattern.search(name) is not None

class GlobLoader(CustomMethodNameLoader):
    "Load test methods matching the glob pattern"
    def __init__(self, pattern):
        CustomMethodNameLoader.__init__(self)
        self.pattern = pattern

    def _testNamePredicate(self, name):
        import fnmatch
        return fnmatch.fnmatch(name, self.pattern)
