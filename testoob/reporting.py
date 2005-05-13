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
        self.errors.append((test, self._exc_info_to_string(err, test)))

    def addFailure(self, test, err):
        self.failures.append((test, self._exc_info_to_string(err, test)))

    def addSuccess(self, test):
        pass

    def _wasSuccessful(self):
        "Tells whether or not this result was a success"
        return len(self.failures) == len(self.errors) == 0

    # Constructing meaningful report strings from exception info

    def _exc_info_to_string(self, err, test):
        "Converts a sys.exc_info()-style tuple of values into a string."
        import traceback
        exctype, value, tb = err
        # Skip test runner traceback levels
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next
        if exctype is test.failureException:
            # Skip assert*() traceback levels
            length = self._count_relevant_tb_levels(tb)
            return ''.join(traceback.format_exception(exctype, value, tb, length))
        return ''.join(traceback.format_exception(exctype, value, tb))

    def _is_relevant_tb_level(self, tb):
        return tb.tb_frame.f_globals.has_key('__unittest')

    def _count_relevant_tb_levels(self, tb):
        length = 0
        while tb and not self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
        return length

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

