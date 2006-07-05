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
import threading
class ProgressBarGuiThread(threading.Thread):
    def __init__(self, num_tests, bar_width):
        threading.Thread.__init__(self)
        self.num_tests = num_tests
        self.bar_width = bar_width
        self.ready_event = threading.Event()

    def wait_until_ready(self):
        self.ready_event.wait()

    def run(self):
        self.root = Tk()
        self.count = 0
        self.textVar = StringVar()
        self.update()
        Label(self.root, textvariable=self.textVar).pack()
        self.ready_event.set()
        self.root.mainloop()

    ratio = property(lambda self: float(self.count) / float(self.num_tests))
    percent = property(lambda self: "%%%d" % int(100 * self.ratio))

    done_bar_length = property( lambda self: int(self.ratio * self.bar_width) )
    left_bar_length = property( lambda self: self.bar_width - self.done_bar_length )

    text_bar = property(
        lambda self: self.done_bar_length * "#" + self.left_bar_length * "_"
    )

    status = property(lambda self: "%s %s" % (self.text_bar, self.percent))
    
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
        self._pbg.wait_until_ready()

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
