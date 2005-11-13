# TestOOB, Python Testing Out Of (The) Box
# Copyright (C) 2005 Ori Peleg, Barak Schiller, and Misha Seltzer
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

"Reporting facilities"

class IReporter:
    "Interface for reporters"
    def start(self):
        "Called when the testing is about to start"
        pass

    def done(self):
        "Called when the testing is done"
        pass

    ########################################
    # Proxied result object methods
    ########################################

    def startTest(self, test):
        "Called when the given test is about to be run"
        pass

    def stopTest(self, test):
        "Called when the given test has been run"
        pass

    def addError(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info()."""
        pass

    def addFailure(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info()."""
        pass

    def addSuccess(self, test):
        "Called when a test has completed successfully"
        pass

    def addAssert(self, test, assertName, varList, err):
        "Called when an assert was made (if err is None, the assert passed)"
        pass

    ########################################
    # Additional reporter's methods.
    ########################################
    def getDescription(self, test):
        "Get a nice printable description of the test"
        pass

    def isSuccessful(self):
        "Tells whether or not this result was a success"
        pass

# Constructing meaningful report strings from exception info

def _exc_info_to_string(err, test):
    "Converts a sys.exc_info()-style tuple of values into a string."
    import traceback
    exctype, value, tb = err
    # Skip test runner traceback levels
    while tb and _is_relevant_tb_level(tb):
        tb = tb.tb_next
    if exctype is test.failureException:
        # Skip assert*() traceback levels
        length = _count_relevant_tb_levels(tb)
        return ''.join(traceback.format_exception(exctype, value, tb, length))
    return ''.join(traceback.format_exception(exctype, value, tb))

def _is_relevant_tb_level(tb):
    return tb.tb_frame.f_globals.has_key('__unittest')

def _count_relevant_tb_levels(tb):
    length = 0
    while tb and not _is_relevant_tb_level(tb):
        length += 1
        tb = tb.tb_next
    return length

def _error_string(test, err):
    """
    Convert the error to a string with _exc_info_to_string unless err
    has already been converted (is a string)
    """
    if isinstance(err, str):
        # error has already been converted
        return err
    return _exc_info_to_string(err, test)


import time as _time
class BaseReporter(IReporter):
    """Base class for most reporters, with a sensible default implementation
    for most of the reporter methods"""
    # borrows a lot of code from unittest.TestResult

    def __init__(self):
        self.testsRun = 0
        self.failures = []
        self.errors = []
        self.asserts = {}

    def start(self):
        self.start_time = _time.time()

    def done(self):
        self.total_time = _time.time() - self.start_time
        del self.start_time

    def startTest(self, test):
        self.testsRun += 1
        self.asserts[test] = []

    def stopTest(self, test):
        pass

    def addError(self, test, err):
        self.errors.append((test, _error_string(test, err)))

    def addFailure(self, test, err):
        self.failures.append((test, _error_string(test, err)))

    def addSuccess(self, test):
        pass

    def addAssert(self, test, assertName, varList, err):
        self.asserts[test] += [(assertName, varList, err)]

    def isSuccessful(self):
        "Tells whether or not this result was a success"
        return len(self.failures) == len(self.errors) == 0
    
class TextStreamReporter(BaseReporter):
    "Reports to a text stream"
    # Modified from unittest._TextTestResult

    separator1 = '=' * 70
    separator2 = '-' * 70

    def __init__(self, stream, descriptions, verbosity, immediate = False):
        import re
        self.re = re
        BaseReporter.__init__(self)
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.vassert = verbosity == 3
        self.immediate = immediate
        self.descriptions = descriptions

    def startTest(self, test):
        BaseReporter.startTest(self, test)
        self.multiLineOutput = False
        if self.showAll:
            self._write(self.getDescription(test))
            self._write(" ... ")

    def addSuccess(self, test):
        BaseReporter.addSuccess(self, test)
        if self.showAll:
            self._write("\n" * self.multiLineOutput)
            self._writeln(self._decorateSuccess("OK"))
        elif self.dots:
            self._write(self._decorateSuccess('.'))

    def addError(self, test, err):
        BaseReporter.addError(self, test, err)
        if self.showAll:
            self._write("\n" * self.multiLineOutput)
            self._writeln(self._decorateFailure("ERROR"))
        elif self.dots:
            self._write(self._decorateFailure('E'))
        if self.immediate:
            self._immediatePrint(test, err, "ERROR")

    def addFailure(self, test, err):
        BaseReporter.addFailure(self, test, err)
        if self.showAll:
            self._write("\n" * self.multiLineOutput)
            self._writeln(self._decorateFailure("FAIL"))
        elif self.dots:
            self._write(self._decorateFailure('F'))
        if self.immediate:
            self._immediatePrint(test, err, "FAIL")

    def stopTest(self, test):
        BaseReporter.stopTest(self, test)
        if self.vassert and not self.immediate:
            self._printVasserts(test)

    def _vassertMessage(self, assertName, varList, isPassed):
        msg = "(" + assertName + ") "
        msg += " ".join([name + ": \"" + str(value) + "\"" for name, value in varList])
        decoratedSign = self._decorateSign(isPassed)
        return "[ %(decoratedSign)s %(msg)s ]" % vars()

    def _printVasserts(self, test):
        for assertName, varList, err in self.asserts[test]:
            self._writeln("  " + self._vassertMessage(assertName, varList, (err == None)))

    def _immediatePrint(self, test, error, flavour):
        if self.dots:
            self._write("\n")
        self._printOneError(flavour, test,  _exc_info_to_string(error, test))
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

    def addAssert(self, test, assertName, varList, err):
        BaseReporter.addAssert(self, test, assertName, varList, err)
        if self.immediate and self.vassert:
            self._write("\n  " + self._vassertMessage(assertName, varList, (err == None)))
            self.multiLineOutput = True

    def _printResults(self):
        testssuffix = self.testsRun > 1 and "s" or ""
        self._writeln("Ran %d test%s in %.3fs" %
                (self.testsRun, testssuffix, self.total_time))

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

    def _printErrors(self):
        if self.dots or self.showAll:
            self._write("\n")
        self._printErrorList('ERROR', self.errors)
        self._printErrorList('FAIL', self.failures)

    def _printErrorList(self, flavour, errors):
        for test, err in errors:
            self._printOneError(flavour, test, err)
            self._write("\n")

    def _printOneError(self, flavour, test, err):
        self._writeln(self.separator1)
        self._writeln(self._decorateFailure("%s: %s" % (flavour,self.getDescription(test))))
        self._writeln(self.separator2)
        self._write("%s" % err)

    def _write(self, s):
        self.stream.write(s)
    def _writeln(self, s):
        self.stream.write(s)
        self.stream.write("\n")

    def getDescription(self, test):
        default_description = test._TestCase__testMethodName + " (" + self.re.sub("^__main__.", "", test.id()) + ")"
        if self.descriptions:
            return test.shortDescription() or default_description
        else:
            return default_description


class ColoredTextReporter(TextStreamReporter):
    "Uses ANSI escape sequences to color the output of a text reporter"
    codes = {"reset":"\x1b[0m",
             "bold":"\x1b[01m",
             "teal":"\x1b[36;06m",
             "turquoise":"\x1b[36;01m",
             "fuscia":"\x1b[35;01m",
             "purple":"\x1b[35;06m",
             "blue":"\x1b[34;01m",
             "darkblue":"\x1b[34;06m",
             "green":"\x1b[32;01m",
             "darkgreen":"\x1b[32;06m",
             "yellow":"\x1b[33;01m",
             "brown":"\x1b[33;06m",
             "red":"\x1b[31;01m",
             "darkred":"\x1b[31;06m"}

    def __init__(self, stream, descriptions, verbosity, immediate):
        TextStreamReporter.__init__(self, stream, descriptions, verbosity, immediate)

    def _red(self, str):
        "Make it red!"
        return ColoredTextReporter.codes['red'] + str + ColoredTextReporter.codes['reset']

    def _green(self, str):
        "make it green!"
        return ColoredTextReporter.codes['green'] + str + ColoredTextReporter.codes['reset']

    def _decorateFailure(self, errString):
        return self._red(errString)

    def _decorateSuccess(self, sccString):
        return self._green(sccString)

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

    def startTest(self, test):
        BaseReporter.startTest(self, test)
        self.test_starts[test] = _time.time()

    def addError(self, test, err):
        BaseReporter.addError(self, test, err)
        self._add_unsuccessful_testcase("error", test, err)

    def addFailure(self, test, err):
        BaseReporter.addFailure(self, test, err)
        self._add_unsuccessful_testcase("failure", test, err)

    _SuccessTemplate='<tr><td>%s</td><td>%s</td><td><font color="green">success</font></td></tr>'
    def addSuccess(self, test):
        BaseReporter.addSuccess(self, test)
        self._sio.write(HTMLReporter._SuccessTemplate%(str(test), self._test_time(test)))

    _FailTemplate="""
    <tr><td>%s</td><td>%s</td><td><font color="red">%s</font></td>
    <td>%s</td></tr>
    """
    def _add_unsuccessful_testcase(self, failure_type, test, err):
        self._sio.write(HTMLReporter._FailTemplate%(str(test), self._test_time(test), failure_type, self._encodeException(_exc_info_to_string(err, test))))

    def _test_time(self, test):
        result = _time.time() - self.test_starts[test]
        del self.test_starts[test]
        return "%.4f" % result


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

    def startTest(self, test):
        BaseReporter.startTest(self, test)
        self.test_starts[test] = _time.time()

    def addError(self, test, err):
        BaseReporter.addError(self, test, err)
        self._add_unsuccessful_testcase("error", test, err)

    def addFailure(self, test, err):
        BaseReporter.addFailure(self, test, err)
        self._add_unsuccessful_testcase("failure", test, err)

    def addSuccess(self, test):
        BaseReporter.addSuccess(self, test)
        self._start_testcase_tag(test)
        self.writer.element("result", "success")
        self.writer.end("testcase")

    def _add_unsuccessful_testcase(self, failure_type, test, err):
        self._start_testcase_tag(test)
        self.writer.element("result", failure_type)
        self.writer.element(failure_type, _exc_info_to_string(err, test), type=str(err[0]), message=str(err[1]))
        self.writer.end("testcase")

    def _start_testcase_tag(self, test):
        self.writer.start("testcase", name=str(test), time=self._test_time(test))

    def _test_time(self, test):
        result = _time.time() - self.test_starts[test]
        del self.test_starts[test]
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

class XSLTReporter(XMLReporter):
    "This reporter uses an XSL transformation scheme to convert an XML output"
    
    class IXSLTApplier:
        "An interface for XSLT libs"
        def __init__(self, transform):
            "A constructor with the transformation to apply (string)"
            pass
        def apply(self, input, params={}):
            """Apply the transformation to the input and return the result.
            Params is a dictionary of extra parameters for the XSLT convertion"""
            pass
    
    class FourSuiteXSLTApplier(IXSLTApplier):
        "XSLT applier that uses 4Suite"
        def __init__(self, transform):
            from Ft.Xml.Xslt import Processor
            from Ft.Xml import InputSource
            self.processor = Processor.Processor()
            trans_source = InputSource.DefaultFactory.fromString(transform, "CONVERTER")
            self.processor.appendStylesheet(trans_source)
        
        def apply(self, input, params={}):
            from Ft.Xml import InputSource
            input_source = InputSource.DefaultFactory.fromString(input, "XML")
            return self.processor.run(input_source, topLevelParams=params)

    class WinCOMXSLTApplier(IXSLTApplier):
        "XSLT applier that uses window's COM interface to use a common windows XML library"
        def __init__(self,transform):
            import win32com.client
            self.trans_obj = win32com.client.Dispatch('Microsoft.XMLDOM')
            self.trans_obj.loadXML(transform)
        
        def apply(self, input, params= {}):
            import win32com.client
            input_obj = win32com.client.Dispatch('Microsoft.XMLDOM')
            input_obj.loadXML(input)
            return input_obj.transformNode(self.trans_obj)
            
   
    def __init__(self, filename, converter):
        XMLReporter.__init__(self)
        self.filename = filename
        self.converter = converter
    def done(self):
        XMLReporter.done(self)
        xslt_applier = self._create_xslt_applier()(self.converter)
        result = xslt_applier.apply(self.get_xml(), params = {u'date': unicode(_time.asctime())})
        open(self.filename, "wt").write(result)
    
    def _create_xslt_applier(self):
        try:
            import win32com.client
            win32com.client.Dispatch('Microsoft.XMLDOM')
            return XSLTReporter.WinCOMXSLTApplier
        except:
            pass
        try:
            import Ft.Xml
            return XSLTReporter.FourSuiteXSLTApplier
        except:
            pass
        raise Exception,"Unable to find supported XSLT library (4Suite, MSXML)"

class HTMLReporter(XSLTReporter):
    def __init__(self, filename):
        import xslconverters
        XSLTReporter.__init__(self, filename, xslconverters.BASIC_CONVERTER)

class PickleFriendlyReporterProxy:
    """
    Used for speaking with remote reporters, where the arguments passed
    must be pickleable.
    The tactic is to convert errors to strings locally and send the final
    string to the remote reporter (tracebacks aren't pickleable).
    """
    def __init__(self, reporter):
        self.reporter = reporter

    # direct proxies
    def addSuccess(self, test):
        self.reporter.addSuccess(test)
    def startTest(self, test):
        self.reporter.startTest(test)
    def stopTest(self, test):
        self.reporter.stopTest(test)

    # making tracebacks safe for pickling
    def addError(self, test, err):
        from testoob import reporting
        self.reporter.addError(test, reporting._exc_info_to_string(err, test))
    def addFailure(self, test, err):
        from testoob import reporting
        self.reporter.addFailure(test, reporting._exc_info_to_string(err, test))

    def addAssert(self, test, assertName, varList, err):
        raise NotImplementedError # TODO: check when we need this


###############################################################################
# Reporter proxy
###############################################################################
def ObserverProxy(method_names):
    """
    Create a thread-safe proxy that forwards methods to a group of observers.
    Each method can return a boolean value, the proxy will return the '&' between them.
    See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/413701.
    """
    class Proxy:
        def __init__(self):
            self.observers = []
            import threading
            self.lock = threading.RLock()
        def add_observer(self, observer):
            self.observers.append(observer)
        def remove_observer(self, observer):
            self.observers.remove(observer)

    def create_method_proxy(method_name):
        def method_proxy(self, *args, **kwargs):
            self.lock.acquire()
            retVal = True
            try:
                for observer in self.observers:
                    retVal &= bool(getattr(observer, method_name)(*args, **kwargs))
            finally:
                self.lock.release()
            return retVal
        return method_proxy

    for method_name in method_names:
        setattr(Proxy, method_name, create_method_proxy(method_name))

    return Proxy

ReporterProxy = ObserverProxy([
    "start",
    "done",
    "startTest",
    "stopTest",
    "addError",
    "addFailure",
    "addSuccess",
    "addAssert",
    "isSuccessful",
])


