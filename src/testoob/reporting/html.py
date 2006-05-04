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

"""
An HTML reporter.

Based on Wai Yip Tung's HTMLTestRunner:
http://tungwaiyip.info/software/HTMLTestRunner.html
"""

raise ImportError("HTMLTestRunner-based HTML reporting is still disabled")

def get_runner(title=None, report_attrs=[], description=None):
    import HTMLTestRunner
    return HTMLTestRunner.HTMLTestRunner(
            title        = title,
            report_attrs = report_attrs,
            description  = description
        )

from base import BaseReporter
class NewHTMLReporter(BaseReporter):
    "Creates an HTML file with the report"
    # Contains code directly from HTMLTestRunner's _TestResult class

    def __init__(self, stream):
        BaseReporter.__init__(self)

        self.stream = stream

        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0

        # result is a list of result in 4 tuple
        # (
        #   result code (0: success; 1: fail; 2: error),
        #   TestCase object,
        #   Test output (byte string),
        #   stack trace,
        # )
        self.result = []

    def addSuccess(self, test_info):
        BaseReporter.addSuccess(self, test_info)
        self.success_count += 1
        self.result.append((0, test_info.classname(), '', ''))

    def addError(self, test_info, err_info):
        BaseReporter.addError(self, test_info, err_info)
        self.error_count += 1
        self.result.append((2, test_info.classname(), '', str(err_info)))

    def addFailure(self, test_info, err_info):
        BaseReporter.addFailure(self, test_info.classname(), err_info)
        self.failure_count += 1
        self.result.append((1, test_info.classname(), '', str(err_info)))

    def done(self):
        BaseReporter.done(self)

        # TODO: deal with runner.startTime and runner.stopTime
        runner = get_runner()
        import datetime
        runner.stopTime = datetime.datetime.now()

        self.stream.write( runner.generateReportString(self) )

