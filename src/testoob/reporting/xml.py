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

"Report results in XML format"

from base import BaseReporter
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
        self.writer.start("results")
        self.writer.start("testsuites")

    def done(self):
        BaseReporter.done(self)

        self.writer.element("total_time", value="%.4f"%self.total_time)
        self.writer.end("testsuites")

        if self.cover_amount is not None and self.cover_amount == "xml":
            self._write_coverage(self.coverage)

        self.writer.end("results")

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

    def _add_testcase_element(self, test_info, result, add_elements = lambda:None):
        self._start_testcase_tag(test_info)
        self.writer.element("result", result)
        add_elements()
        self.writer.end("testcase")

    def addSuccess(self, test_info):
        BaseReporter.addSuccess(self, test_info)
        self._add_testcase_element(test_info, "success")

    def addSkip(self, test_info, err_info):
        BaseReporter.addSkip(self, test_info, err_info)
        def add_elements():
            self.writer.element( "reason", err_info.exception_value() )
        self._add_testcase_element(test_info, "skip")

    def _add_unsuccessful_testcase(self, failure_type, test_info, err_info):
        def add_elements():
            "Additional elements specific for failures and errors"
            self.writer.element(failure_type, str(err_info), type=err_info.exception_type(), message=err_info.exception_value())
        self._add_testcase_element(test_info, failure_type, add_elements)

    def _start_testcase_tag(self, test_info):
        self.writer.start("testcase", name=str(test_info), time=self._test_time(test_info))

    def _test_time(self, test_info):
        result = time.time() - self.test_starts[test_info]
        del self.test_starts[test_info]
        return "%.4f" % result

    def _write_coverage(self, coverage):
        self.writer.start("coverage")
        for filename, stats in coverage.getstatistics().items():
            # TODO: can probably extract loop body to a method
            self.writer.start("sourcefile", name=filename,
                              statements=str(stats["lines"]),
                              executed=str(stats["covered"]),
                              percent=str(stats["percent"]))
            lines, covered =  coverage.coverage[filename].values()
            missing = [line for line in covered if line not in lines]
            self.writer.data(str(missing)[1:-1].replace(" ", ""))
            self.writer.end("sourcefile")
        self.writer.end("coverage")

class XMLFileReporter(XMLReporter):
    def __init__(self, filename):
        XMLReporter.__init__(self)
        self.filename = filename

    def done(self):
        XMLReporter.done(self)

        f = file(self.filename, "w")
        try: f.write(self.get_xml())
        finally: f.close()
