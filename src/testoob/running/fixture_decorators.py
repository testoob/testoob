# Testoob, Python Testing Out Of (The) Box
# Copyright (C) 2005 The Testoob Team
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

"Decorators for standard fixtures"

class BaseFixture:
    def __init__(self, fixture):
        self.fixture = fixture

    def __call__(self, *args):
        self.fixture(*args)

    def get_fixture(self):
        result = self.fixture
        while hasattr(result, "get_fixture"):
            result = result.get_fixture()
        return result

class ManipulativeFixture(BaseFixture):
    def __init__(self, fixture):
        BaseFixture.__init__(self, fixture)
        self.coreFixture = self.get_fixture()
        self.testMethodName = self.coreFixture.id().split(".")[-1]
        self.testMethod = getattr(self.coreFixture, self.testMethodName)

    def updateMethod(self, newMethod):
        setattr(self.coreFixture, self.testMethodName, newMethod)

def get_alarmed_fixture(timeout):
    class AlarmedFixture(BaseFixture):
        def __init__(self, fixture):
            BaseFixture.__init__(self, fixture)
            from signal import alarm
            self.alarm = alarm
        
        def __call__(self, *args):
            self.alarm(timeout) # Set timeout for a fixture.
            BaseFixture.__call__(self, *args)
            self.alarm(0) # Release the alarm that was set.
    return AlarmedFixture

def _fix_sourcefile_extension(filename):
    # from Python's logging module
    # TODO: support py2exe?
    #import sys
    #if hasattr(sys, 'frozen'): #support for py2exe
    #    return "logging%s__init__%s" % (os.sep, filename[-4:])
    if filename[-4:].lower() in ['.pyc', '.pyo']:
        return filename[:-4] + '.py'
    return filename
def _fix_sourcefile(filename):
    from os.path import normcase, abspath
    return abspath(normcase(_fix_sourcefile_extension(filename)))
def _module_sourcefile(module_name):
    return _fix_sourcefile(__import__(module_name).__file__)

def get_coverage_fixture(coverage):
    from os.path import abspath
    class CoveredFixture(BaseFixture):
        def __init__(self, fixture):
            BaseFixture.__init__(self, fixture)
            coverage.ignorepaths.append(_module_sourcefile(fixture.__module__))

        def __call__(self, *args):
            coverage.runfunc(BaseFixture.__call__, self, *args)
    return CoveredFixture

def get_timed_fixture(time_limit):
    class TimedFixture(ManipulativeFixture):
        def __init__(self, fixture):
            ManipulativeFixture.__init__(self, fixture)
            def timedTest():
                from time import time
                start = time()
                while time() - start < time_limit:
                    self.testMethod()
            self.updateMethod(timedTest)
    return TimedFixture

def get_capture_fixture():
    class CaptureFixture(ManipulativeFixture):
        def __init__(self, fixture):
            ManipulativeFixture.__init__(self, fixture)
            def CaptureTest():
                import sys, os
                stdout_fh = sys.stdout
                stderr_fh = sys.stderr
                (read_fd, write_fd) = os.pipe()
                writer = os.fdopen(write_fd, "w")
                reader = os.fdopen(read_fd,  "r")
                sys.stdout = sys.stderr = writer
                try:
                    self.testMethod()
                finally:
                    writer.close()
                    self.coreFixture._testOOB_output_txt = reader.read()
                    reader.close()
                    sys.stdout = stdout_fh
                    sys.stderr = stderr_fh
            self.updateMethod(CaptureTest)
    return CaptureFixture
