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

"Helper for processed running"

class ProcessedRunnerHelper:
    "A helper class to make ProcessedRunner shorter and clearer."
    def __init__(self, max_processes):
        self._fixturesList = [[] for i in xrange(max_processes)]
        self._load_balance_idx = 0

    def register_fixture(self, fixture):
        self._fixturesList[self._load_balance_idx].append(fixture)
        self._load_balance_idx = (self._load_balance_idx + 1) % len(self._fixturesList)

    def start(self, reporter):
        from os import fork, pipe, fdopen, waitpid
        from sys import exit

        children = []

        for processFixtures in self._fixturesList:
            pid = fork()
            if pid == 0:
                self._run_fixtures(processFixtures, reporter)
                exit()
            children.append(pid)

        for child in children:
            waitpid(child, 0)

    def _run_fixtures(self, fixtures, reporter):
        [fixture(reporter) for fixture in fixtures]

