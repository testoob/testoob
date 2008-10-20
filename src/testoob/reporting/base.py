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

"Useful base class for reporters"

class IReporter:
    "Interface for reporters"

    def setParameters(self, **parameters):
        "Set parameters for the reporter. Called before 'start' is called."

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

    def eraseTest(self, test_info):
        "Called when the given test shouldn't have been registered"
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

    def setCoverageInfo(self, cover_amount, coverage):
        "Sets the coverage info for the reporter"

    def addSkip(self, test_info, err_info, isRegistered=True):
        "Called when the test was skipped"

import time as _time
class BaseReporter(IReporter):
    """Base class for most reporters, with a sensible default implementation
    for most of the reporter methods"""
    # borrows a lot of code from unittest.TestResult

    def __init__(self):
        self.testsRun = 0
        self.successes = []
        self.failures = []
        self.errors = []
        self.skips = []
        self.asserts = {}
	self.start_times = {}
	self.total_times = {}
        self.cover_amount = None
        self.coverage = None

    def setParameters(self, **parameters):
        self.parameters = parameters

    def start(self):
        self.reporter_start_time = _time.time()

    def done(self):
        self.total_time = _time.time() - self.reporter_start_time
        del self.reporter_start_time

    def startTest(self, test_info):
        self.testsRun += 1
        self.asserts[test_info] = []
	self.start_times[test_info] = _time.time()

    def stopTest(self, test_info):
        self.current_test_total_time = _time.time() - self.start_times.pop(test_info)

    def addError(self, test_info, err_info):
        self.errors.append((test_info, err_info))

    def addFailure(self, test_info, err_info):
        self.failures.append((test_info, err_info))

    def addSuccess(self, test_info):
        self.successes.append(test_info)

    def addSkip(self, test_info, err_info, isRegistered=True):
        self.skips.append((test_info, err_info))
        # We don't want to count skipped tests.
        if isRegistered:
            self.testsRun -= 1

    def addAssert(self, test_info, assertName, varList, exception):
        self.asserts[test_info].append((assertName, varList, exception))

    def isSuccessful(self):
        "Tells whether or not this result was a success"
        if len(self.failures)   > 0: return False
        if len(self.errors)     > 0: return False
        if len(self.successes) == 0: return False
        return True

    def setCoverageInfo(self, cover_amount, coverage):
        self.cover_amount = cover_amount
        self.coverage = coverage

    def getTestsOutput(self, test_info):
        "Get the output (stdout and stderr) captured from the test"
        try:
            return test_info.fixture._testOOB_output_txt
        except AttributeError:
            return ""

