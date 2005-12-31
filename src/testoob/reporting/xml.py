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

"Report results in XML format"

from base import BaseReporter
from common import exc_info_to_string
import time
class XMLReporter(BaseReporter):
    """Reports test results in XML, in a format resembling Ant's JUnit xml
    formatting output."""
    def __init__(self):
        BaseReporter.__init__(self)

        from cStringIO import StringIO
        self._sio = StringIO()
        try:
            from elementtree.SimpleXMLWriter import XMLWriter
        except ImportError:
            from compatibility.SimpleXMLWriter import XMLWriter
        self.writer = XMLWriter(self._sio, "utf-8")

        self.test_starts = {}

    def start(self):
        BaseReporter.start(self)
        self.writer.start("testsuites")

    def done(self):
        BaseReporter.done(self)
        self.writer.element("total_time", value="%.4f"%self.total_time)
        self.writer.end("testsuites")

        assert len(self.test_starts) == 0

    def get_xml(self):
        return self._sio.getvalue()

    def startTest(self, test_info):
        BaseReporter.startTest(self, test_info)
        self.test_starts[test_info] = time.time()

    def addError(self, test_info, err_info):
        BaseReporter.addError(self, test_info, err_info)
        self._add_unsuccessful_testcase("error", test_info, err_info)

    def addFailure(self, test_info, err_info):
        BaseReporter.addFailure(self, test_info, err_info)
        self._add_unsuccessful_testcase("failure", test_info, err_info)

    def addSuccess(self, test_info):
        BaseReporter.addSuccess(self, test_info)
        self._start_testcase_tag(test_info)
        self.writer.element("result", "success")
        self.writer.end("testcase")

    def _add_unsuccessful_testcase(self, failure_type, test_info, err_info):
        self._start_testcase_tag(test_info)
        self.writer.element("result", failure_type)
        self.writer.element(failure_type, str(err_info), type=err_info.exception_type(), message=err_info.exception_value())
        self.writer.end("testcase")

    def _start_testcase_tag(self, test_info):
        self.writer.start("testcase", name=str(test_info), time=self._test_time(test_info))

    def _test_time(self, test_info):
        result = time.time() - self.test_starts[test_info]
        del self.test_starts[test_info]
        return "%.4f" % result

class XMLFileReporter(XMLReporter):
    def __init__(self, filename):
        XMLReporter.__init__(self)
        self.filename = filename

    def done(self):
        XMLReporter.done(self)

        f = file(self.filename, "w")
        try: f.write(self.get_xml())
        finally: f.close()


