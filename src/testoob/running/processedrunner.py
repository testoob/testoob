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

"Run tests in processes"

from baserunner import BaseRunner

class ProcessedRunner(BaseRunner):
    "Run tests using fork in different processes."
    def __init__(self, max_processes=1):
        from processed_helper import ProcessedRunnerHelper
        BaseRunner.__init__(self)
        self._helper = ProcessedRunnerHelper(max_processes)

    def run(self, fixture):
        BaseRunner.run(self, fixture)
        self._helper.register_fixture(fixture)

    def done(self):
        self._helper.start(self.reporter)
        BaseRunner.done(self)
