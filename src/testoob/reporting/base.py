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

    def startTest(self, test_info):
        "Called when the given test is about to be run"
        pass

    def stopTest(self, test_info):
        "Called when the given test has been run"
        pass

    def addError(self, test_info, err_info):
        """
        Called when an error has occurred.

        @param test_info a TestInfo instance
        @param err_info an ErrInfo instance
        """
        pass

    def addFailure(self, test_info, err_info):
        """
        Called when a failure has occurred.
        
        @param test_info a TestInfo instance
        @param err_info an ErrInfo instance
        """
        pass

    def addSuccess(self, test_info):
        "Called when a test has completed successfully"
        pass

    def addAssert(self, test_info, assertName, varList, exception):
        "Called when an assert was made (if exception is None, the assert passed)"
        pass

    ########################################
    # Additional reporter's methods.
    ########################################
    def getDescription(self, test_info):
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

    def startTest(self, test_info):
        self.testsRun += 1
        self.asserts[test_info] = []

    def stopTest(self, test_info):
        pass

    def addError(self, test_info, err_info):
        self.errors.append((test_info, err_info))

    def addFailure(self, test_info, err_info):
        self.failures.append((test_info, err_info))

    def addSuccess(self, test_info):
        pass

    def addAssert(self, test_info, assertName, varList, exception):
        # TODO: append?
        self.asserts[test_info] += [(assertName, varList, exception)]

    def isSuccessful(self):
        "Tells whether or not this result was a success"
        return len(self.failures) == len(self.errors) == 0


