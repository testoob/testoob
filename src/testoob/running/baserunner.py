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

import testoob.asserter

class BaseRunner(object):
    """default implementations of setting a reporter and done()"""
    def __init__(self):
        self.reporter = None

    def run(self, fixture):
        # Let the assert functions know its reporter
        testoob.asserter.Asserter().set_reporter(fixture.get_fixture(), self.reporter)

    def done(self):
        self.reporter.done()

    def isSuccessful(self):
        return self.reporter.isSuccessful()
