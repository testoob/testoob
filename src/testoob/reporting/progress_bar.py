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
    def __init__(self, num_tests, bar_width):
        Thread.__init__(self)
        self.num_tests = num_tests
        self.bar_width = bar_width

    def run(self):
        self.root = Tk()
        self.count = 0
        self.textVar = StringVar()
        self.update()
        Label(self.root, textvariable=self.textVar).pack()
        self.root.mainloop()

    ratio = property(lambda self: float(self.count) / float(self.num_tests))
    percent = property(lambda self: "%%%d" % int(100 * self.ratio))

    text_bar = property(lambda self: self.x)

    status = property(lambda self: self.percent)
    
    def advance(self):
        self.count += 1
        self.update()

    def die(self):
        self.root.quit()

        # Tk complains when __del__ is called from different thread
        del self.root, self.textVar

    def update(self):
        self.textVar.set(self.status)

from base import BaseReporter
class ProgressBarReporter(BaseReporter):
    "Displays a progress bar"

    BAR_WIDTH = 30

    def start(self):
        BaseReporter.start(self)
        self._pbg = ProgressBarGuiThread(
            num_tests=self.parameters["num_tests"],
            bar_width = self.BAR_WIDTH,
        )
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
