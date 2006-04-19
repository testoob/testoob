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

"Useful base class for runners"

class BaseRunner(object):
    """default implementations of setting a reporter and done()"""
    def __init__(self):
        from testoob.asserter import Asserter
        self._Asserter = Asserter

    def _set_reporter(self, reporter):
        self._reporter = reporter
        self._reporter.start()
    reporter = property(lambda self:self._reporter, _set_reporter)

    def run(self, fixture):
        # Let the assert functions know it's reporter.
        self._Asserter().set_reporter(fixture.get_fixture(), self._reporter)

    def done(self):
        self.reporter.done()

    def isSuccessful(self):
        return self.reporter.isSuccessful()

class SimpleRunner(BaseRunner):
    def run(self, fixture):
        BaseRunner.run(self, fixture)
        fixture(self._reporter)
        return self._reporter.isSuccessful()

