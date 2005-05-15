class IReporter:
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

import time as _time
class BaseReporter(IReporter):
    "Interface for reporters"
    # Borrows most of its code from unittest.TestResult
    
    def __init__(self):
        self.testsRun = 0
        self.failures = []
        self.errors = []

    def start(self):
        self.start_time = _time.time()

    def done(self):
        self.total_time = _time.time() - self.start_time
        del self.start_time

    def startTest(self, test):
        self.testsRun += 1

    def stopTest(self, test):
        pass

    def addError(self, test, err):
        self.errors.append((test, _exc_info_to_string(err, test)))

    def addFailure(self, test, err):
        self.failures.append((test, _exc_info_to_string(err, test)))

    def addSuccess(self, test):
        pass

    def _wasSuccessful(self):
        "Tells whether or not this result was a success"
        return len(self.failures) == len(self.errors) == 0


class TextStreamReporter(BaseReporter):
    "Reports to a text stream"
    # Modified from unittest._TextTestResult

    separator1 = '=' * 70
    separator2 = '-' * 70
    
    def __init__(self, stream, descriptions, verbosity):
        BaseReporter.__init__(self)
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.descriptions = descriptions

    def startTest(self, test):
        BaseReporter.startTest(self, test)
        if self.showAll:
            self._write(self._getDescription(test))
            self._write(" ... ")

    def addSuccess(self, test):
        BaseReporter.addSuccess(self, test)
        if self.showAll:
            self._writeln("ok")
        elif self.dots:
            self._write('.')

    def addError(self, test, err):
        BaseReporter.addError(self, test, err)
        if self.showAll:
            self._writeln("ERROR")
        elif self.dots:
            self._write('E')

    def addFailure(self, test, err):
        BaseReporter.addFailure(self, test, err)
        if self.showAll:
            self._writeln("FAIL\n")
        elif self.dots:
            self._write('F')

    def done(self):
        BaseReporter.done(self)
        self._printErrors()
        self._writeln(self.separator2)
        self._printResults()

    def _printResults(self):
        testssuffix = self.testsRun > 1 and "s" or ""
        self._writeln("Ran %d test%s in %.3fs" %
                (self.testsRun, testssuffix, self.total_time))

        if self._wasSuccessful():
            self._writeln("OK")
        else:
            strings = []
            if len(self.failures) > 0:
                strings.append("failures=%d" % len(self.failures))
            if len(self.errors) > 0:
                strings.append("errors=%d" % len(self.errors))

            self._writeln("FAILED (%s)" % ", ".join(strings))

    def _printErrors(self):
        if self.dots or self.showAll:
            self._write("\n")
        self._printErrorList('ERROR', self.errors)
        self._printErrorList('FAIL', self.failures)

    def _printErrorList(self, flavour, errors):
        for test, err in errors:
            self._writeln(self.separator1)
            self._writeln("%s: %s" % (flavour,self._getDescription(test)))
            self._writeln(self.separator2)
            self._writeln("%s" % err)

    def _write(self, s):
        self.stream.write(s)
    def _writeln(self, s):
        self.stream.write(s)
        self.stream.write("\n")

    def _getDescription(self, test):
        if self.descriptions:
            return test.shortDescription() or str(test)
        else:
            return str(test)

class XMLReporter(BaseReporter):
    def __init__(self, filename):
        BaseReporter.__init__(self)

        self.filename = filename

        from cStringIO import StringIO
        self._sio = StringIO()
        from elementtree.SimpleXMLWriter import XMLWriter
        self.writer = XMLWriter(self._sio, "utf-8")

        self.test_starts = {}

    def start(self):
        BaseReporter.start(self)
        self.writer.start("testsuites")

    def done(self):
        BaseReporter.done(self)
        self.writer.end("testsuites")

        f = file(self.filename, "w")
        try: f.write(self.get_xml())
        finally: f.close()

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
        self.writer.end("testcase")

    def _add_unsuccessful_testcase(self, failure_type, test, err):
        self._start_testcase_tag(test)
        self.writer.element(failure_type, _exc_info_to_string(err, test))
        self.writer.end("testcase")

    def _start_testcase_tag(self, test):
        self.writer.start("testcase", name=str(test), time=self._test_time(test))

    def _test_time(self, test):
        result = _time.time() - self.test_starts[test]
        del self.test_starts[test]
        return "%.4f" % result

###############################################################################
# Reporter proxy
###############################################################################
def ObserverProxy(method_names):
    class Proxy:
        def __init__(self):
            self._observers = []
        def add_observer(self, observer):
            self._observers.append(observer)
        def remove_observer(self, observer):
            self._observers.remove(observer)

    def create_method_proxy(method_name):
        def method_proxy(self, *args, **kwargs):
            for observer in self._observers:
                getattr(observer, method_name)(*args, **kwargs)
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
])


