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

"Useful base class for reporters"

class IReporter:
    "Interface for reporters"
    def start(self):
        "Called when the testing is about to start"
        pass

    def done(self):
        "Called when the testing is done"
        pass

    ########################################
    # Proxied result object methods
    ########################################

    def startTest(self, test):
        "Called when the given test is about to be run"
        pass

    def stopTest(self, test):
        "Called when the given test has been run"
        pass

    def addError(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info()."""
        pass

    def addFailure(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info()."""
        pass

    def addSuccess(self, test):
        "Called when a test has completed successfully"
        pass

    def addAssert(self, test, assertName, varList, err):
        "Called when an assert was made (if err is None, the assert passed)"
        pass

    ########################################
    # Additional reporter's methods.
    ########################################
    def getDescription(self, test):
        "Get a nice printable description of the test"
        pass

    def isSuccessful(self):
        "Tells whether or not this result was a success"
        pass


import time as _time
from common import _error_string
class BaseReporter(IReporter):
    """Base class for most reporters, with a sensible default implementation
    for most of the reporter methods"""
    # borrows a lot of code from unittest.TestResult

    def __init__(self):
        self.testsRun = 0
        self.failures = []
        self.errors = []
        self.asserts = {}

    def start(self):
        self.start_time = _time.time()

    def done(self):
        self.total_time = _time.time() - self.start_time
        del self.start_time

    def startTest(self, test):
        self.testsRun += 1
        self.asserts[test] = []

    def stopTest(self, test):
        pass

    def addError(self, test, err):
        self.errors.append((test, _error_string(test, err)))

    def addFailure(self, test, err):
        self.failures.append((test, _error_string(test, err)))

    def addSuccess(self, test):
        pass

    def addAssert(self, test, assertName, varList, err):
        self.asserts[test] += [(assertName, varList, err)]

    def isSuccessful(self):
        "Tells whether or not this result was a success"
        return len(self.failures) == len(self.errors) == 0


