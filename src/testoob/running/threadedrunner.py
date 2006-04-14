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

"Run tests in multiple threads"

from baserunner import BaseRunner

class ThreadedRunner(BaseRunner):
    "Run tests using a threadpool"

    def __init__(self, num_threads):
        BaseRunner.__init__(self)
        from threadpool import ThreadPool
        self.pool = ThreadPool(num_threads)
        self.pool.start()

    def run(self, fixture):
        BaseRunner.run(self, fixture)
        self.pool.dispatch(fixture, self.reporter)

    def done(self):
        self.pool.stop()
        BaseRunner.done(self)
