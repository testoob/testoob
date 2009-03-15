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

"The proxy used as a result object for PyUnit suites"

# TODO: separate the PyUnit result-object passed to the fixtures and
#       the observable proxy that proxies everything to reporters.
#       Notice the '_apply_method' duplication in each method, this should
#       be removed.

from test_info import create_test_info
from err_info import create_err_info

def synchronize(func, lock=None):
    if lock is None:
        import threading
        lock = threading.RLock()

    def wrapper(*args, **kwargs):
        lock.acquire()
        try:
            return func(*args, **kwargs)
        finally:
            lock.release()

    return wrapper

class ReporterProxy:
    def __init__(self, threads=False):
        self.observing_reporters = []

        if threads:
            self._apply_method = synchronize(self._apply_method)

    def add_observer(self, reporter):
        self.observing_reporters.append(reporter)

    def _apply_method(self, name, *args, **kwargs):
        for reporter in self.observing_reporters:
            getattr(reporter, name)(*args, **kwargs)

    def setParameters(self, **parameters):
        self._apply_method("setParameters", **parameters)

    def start(self):
        self._apply_method("start")

    def done(self):
        self._apply_method("done")

    def startTest(self, test):
        self._apply_method("startTest", create_test_info(test))

    def stopTest(self, test):
        self._apply_method("stopTest", create_test_info(test))

    def addError(self, test, err):
        test_info = create_test_info(test)
        err_info = create_err_info(test, err)

        if err_info.is_skip():
            self._apply_method("addSkip", test_info, err_info)
            return

        self._apply_method("addError", test_info, err_info)

    def addFailure(self, test, err):
        self._apply_method("addFailure", create_test_info(test), create_err_info(test, err))

    def addSuccess(self, test):
        self._apply_method("addSuccess", create_test_info(test))

    def addAssert(self, test, assertName, varList, exception):
        self._apply_method("addAssert", create_test_info(test), assertName, varList, exception)

    def addSkip(self, test, err, isRegistered=True):
        self._apply_method("addSkip", create_test_info(test), create_err_info(test, err), isRegistered)

    def isSuccessful(self):
        for reporter in self.observing_reporters:
            if not reporter.isSuccessful():
                return False # One failed reporter is enough
        return True

    def isFailed(self):
        for reporter in self.observing_reporters:
            if hasattr(reporter,'isFailed'):
                if reporter.isFailed():
                    return True # One failed reporter is enough
            else:
                if not reporter.isSuccessful():
                    return True
        return False
