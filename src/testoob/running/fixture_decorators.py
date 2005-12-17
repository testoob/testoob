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

"Decorators for standart fixtures"

class BaseFixture:
    def __init__(self, fixture):
        self.fixture = fixture

    def __call__(self, *args):
        self.fixture(*args)

    def get_fixture(self):
        result = self.fixture
        while hasattr(result, "get_fixture"):
            result = result.get_fixture()
        return result

def get_alarmed_fixture(timeout):
    class AlarmedFixture(BaseFixture):
        def __init__(self, fixture):
            BaseFixture.__init__(self, fixture)
            from signal import alarm
            self.alarm = alarm
        
        def __call__(self, *args):
            self.alarm(timeout) # Set timeout for a fixture.
            BaseFixture.__call__(self, *args)
            self.alarm(0) # Release the alarm that was set.
    return AlarmedFixture

def get_timed_fixture(time_limit):
    class TimedFixture(BaseFixture):
        def __init__(self, fixture):
            BaseFixture.__init__(self, fixture)
            coreFixture = self.get_fixture()
            testMethodName = coreFixture.id().split(".")[-1]
            testMethod = getattr(coreFixture, testMethodName)
            def timedTest():
                from time import time
                start = time()
                while time() - start < time_limit:
                    testMethod()
            setattr(coreFixture, testMethodName, timedTest)
    return TimedFixture

