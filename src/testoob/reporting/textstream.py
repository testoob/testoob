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

"A text-stream reporter, the most commonly-used kind"

from base import BaseReporter
class TextStreamReporter(BaseReporter):
    "Reports to a text stream"
    # Modified from unittest._TextTestResult
	# TODO: could be refactored quite a bit

    separator1 = '=' * 70
    separator2 = '-' * 70

    def __init__(self, stream, descriptions, verbosity, immediate = False, coverage = (None, None)):
        import re
        self.re = re
        BaseReporter.__init__(self)
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.vassert = verbosity == 3
        self.immediate = immediate
        self.descriptions = descriptions
        self.cover_amount, self.coverage = coverage

    def startTest(self, test_info):
        BaseReporter.startTest(self, test_info)
        self.multiLineOutput = False
        if self.showAll:
            self._write(self.getDescription(test_info))
            self._write(" ... ")

    def addSuccess(self, test_info):
        BaseReporter.addSuccess(self, test_info)
        if self.showAll:
            self._write("\n" * self.multiLineOutput)
            self._writeln(self._decorateSuccess("OK"))
        elif self.dots:
            self._write(self._decorateSuccess('.'))

    def addError(self, test_info, err_info):
        BaseReporter.addError(self, test_info, err_info)
        if self.showAll:
            self._write("\n" * self.multiLineOutput)
            self._writeln(self._decorateFailure("ERROR"))
        elif self.dots:
            self._write(self._decorateFailure('E'))
        if self.immediate:
            self._immediatePrint(test_info, err_info, "ERROR")

    def addFailure(self, test_info, err_info):
        BaseReporter.addFailure(self, test_info, err_info)
        if self.showAll:
            self._write("\n" * self.multiLineOutput)
            self._writeln(self._decorateFailure("FAIL"))
        elif self.dots:
            self._write(self._decorateFailure('F'))
        if self.immediate:
            self._immediatePrint(test_info, err_info, "FAIL")

    def stopTest(self, test_info):
        BaseReporter.stopTest(self, test_info)
        if self.vassert and not self.immediate:
            self._printVasserts(test_info)

    def _vassertMessage(self, assertName, varList, isPassed):
        msg = "(" + assertName + ") "
        msg += " ".join([name + ": \"" + str(value) + "\"" for name, value in varList])
        decoratedSign = self._decorateSign(isPassed)
        return "[ %(decoratedSign)s %(msg)s ]" % vars()

    def _printVasserts(self, test_info):
        for assertName, varList, exception in self.asserts[test_info]:
            self._writeln("  " + self._vassertMessage(assertName, varList, exception is None))

    def _immediatePrint(self, test_info, err_info, flavour):
        if self.dots:
            self._write("\n")
        self._printOneError(flavour, test_info, err_info)
        self._writeln(self.separator1)
        if self.showAll:
            self._write("\n")

    def done(self):
        BaseReporter.done(self)
        if not self.immediate:
            self._printErrors()
        else:
            self._write("\n")
        self._writeln(self.separator2)
        self._printResults()

    def addAssert(self, test_info, assertName, varList, exception):
        BaseReporter.addAssert(self, test_info, assertName, varList, exception)
        if self.immediate and self.vassert:
            self._write("\n  " + self._vassertMessage(assertName, varList, exception is None))
            self.multiLineOutput = True

    def _printResults(self):
        testssuffix = self.testsRun > 1 and "s" or ""
        self._write("Ran %d test%s in %.3fs" %
                (self.testsRun, testssuffix, self.total_time))
        if self.cover_amount is not None:
            self._write(" (covered %s%% of the code)" % self.coverage.total_coverage_percentage())
        self._write("\n")

        if self.isSuccessful():
            self._writeln(self._decorateSuccess("OK"))
        else:
            strings = []
            if len(self.failures) > 0:
                strings.append("failures=%d" % len(self.failures))
            if len(self.errors) > 0:
                strings.append("errors=%d" % len(self.errors))

            self._writeln(self._decorateFailure("FAILED (%s)" % ", ".join(strings)))

    def _decorateSign(self, isPassed):
        if isPassed:
            return self._decorateSuccess("PASSED")
        else:
            return self._decorateFailure("FAILED")

    def _decorateFailure(self, errString):
        return errString

    def _decorateSuccess(self, sccString):
        return sccString

    def _decorateWarning(self, warString):
        return warString

    def _printErrors(self):
        if self.dots or self.showAll:
            self._write("\n")
        self._printErrorList('ERROR', self.errors)
        self._printErrorList('FAIL', self.failures)

    def _printErrorList(self, flavour, errors):
        for test_info, err_info in errors:
            self._printOneError(flavour, test_info, err_info)
            self._write("\n")

    def _printOneError(self, flavour, test_info, err_info):
        self._writeln(self.separator1)
        self._writeln(self._decorateFailure("%s: %s" % (flavour,self.getDescription(test_info))))
        self._writeln(self.separator2)
        self._write(str(err_info))
        output = self.getTestsOutput(test_info)
        if output != "":
            self._writeln(self.separator1)
            self._writeln(self._decorateWarning("Run's output"))
            self._writeln(self.separator2)
            self._write(output)

    def _write(self, s):
        self.stream.write(s)
    def _writeln(self, s):
        self.stream.write(s)
        self.stream.write("\n")

    def getDescription(self, test_info):
        default_description = test_info.funcname() + " (" + self.re.sub("^__main__.", "", test_info.id()) + ")"
        if self.descriptions:
            return test_info.short_description() or default_description
        else:
            return default_description



