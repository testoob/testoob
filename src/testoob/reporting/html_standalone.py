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

"Standalone HTML reporting, doesn't need external XSLT services"

from base import BaseReporter
class OldHTMLReporter(BaseReporter):
    "Direct HTML reporting. Deprecated in favor of XSLT reporting"
    def __init__(self, filename):
        BaseReporter.__init__(self)

        from cStringIO import StringIO
        self._sio = StringIO()
        from elementtree.SimpleXMLWriter import XMLWriter
        self.writer = XMLWriter(self._sio, "utf-8")
        self.filename = filename

        self.test_starts = {}

    def start(self):
        BaseReporter.start(self)
        self._writeHeader()

    def _writeHeader(self):
        self.writer.start("html")
        self.writer.start("head")
        self.writer.element("title", "TESTOOB unit-test report")
        self.writer.end("head")
        self.writer.start("body")
        self.writer.start("table", border="1")
        self.writer.start("tr")
        self.writer.element("td", "Test Name")
        self.writer.element("td", "Time")
        self.writer.element("td", "Result")
        self.writer.element("td", "More info")
        self.writer.end("tr")

    def done(self):
        BaseReporter.done(self)
        self.writer.end("table")
        self.writer.element("p", "Total time: %.4f"%self.total_time)
        self.writer.end("body")
        self.writer.end("html")

        #assert len(self.test_starts) == 0
        f = file(self.filename, "w")
        try: f.write(self._getHtml())
        finally: f.close()

    def _getHtml(self):
        return self._sio.getvalue()

    def _encodeException(self, str):
        import re
        str = re.sub(r'File "(.+)",', r'<a href="file:///\1"> File "\1",</a>', str)
        return str.replace("\n","<br>")

    def startTest(self, test_info):
        BaseReporter.startTest(self, test_info)
        self.test_starts[test_info] = _time.time()

    def addError(self, test_info, err):
        BaseReporter.addError(self, test_info, err)
        self._add_unsuccessful_testcase("error", test_info, err)

    def addFailure(self, test_info, err):
        BaseReporter.addFailure(self, test_info, err)
        self._add_unsuccessful_testcase("failure", test_info, err)

    _SuccessTemplate='<tr><td>%s</td><td>%s</td><td><font color="green">success</font></td></tr>'
    def addSuccess(self, test_info):
        BaseReporter.addSuccess(self, test_info)
        self._sio.write(HTMLReporter._SuccessTemplate%(str(test_info), self._test_time(test_info)))

    _FailTemplate="""
    <tr><td>%s</td><td>%s</td><td><font color="red">%s</font></td>
    <td>%s</td></tr>
    """
    def _add_unsuccessful_testcase(self, failure_type, test_info, err):
        self._sio.write(HTMLReporter._FailTemplate%(str(test_info), self._test_time(test_info), failure_type, self._encodeException(_exc_info_to_string(err, test_info))))

    def _test_time(self, test_info):
        result = _time.time() - self.test_starts[test_info]
        del self.test_starts[test_info]
        return "%.4f" % result


