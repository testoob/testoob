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

"Simple GUI progress bar"

from Tkinter import *
from threading import Thread
class ProgressBarGuiThread(Thread):
    def __init__(self, num_tests):
        Thread.__init__(self)
        self._num_tests = num_tests

    def run(self):
        self._root = Tk()
        self._count = 0
        self._textVar = StringVar()
        self._textVar.set(self.percent_string)
        Label(self._root, textvariable=self._textVar).pack()
        self._root.mainloop()

    percent = property(lambda self: 100 * self._count / self._num_tests)
    percent_string = property( lambda self: "%%%3d" % self.percent )
    
    def advance(self):
        self._count += 1
        self._textVar.set(self.percent_string)

    def die(self):
        self._root.quit()

        # Tk complains when __del__ is called from different thread
        del self._root, self._textVar

from base import BaseReporter
class ProgressBarReporter(BaseReporter):
    "Displays a progress bar"
    def start(self):
        BaseReporter.start(self)
        self._pbg = ProgressBarGuiThread(num_tests=self.parameters["num_tests"])
        self._pbg.start()

    def done(self):
        BaseReporter.done(self)
        self._pbg.die()

    def addError(self, test_info, err_info):
        BaseReporter.addError(self, test_info, err_info)
        self._pbg.advance()

    def addFailure(self, test_info, err_info):
        BaseReporter.addFailure(self, test_info, err_info)
        self._pbg.advance()

    def addSuccess(self, test_info):
        BaseReporter.addSuccess(self, test_info)
        self._pbg.advance()

    def addSkip(self, test_info, err_info):
        BaseReporter.addSkip(self, test_info, err_info)
        self._pbg.advance()
