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

"main() implementation"

def _arg_parser(usage):
    try:
        import optparse
    except ImportError:
        from compatibility import optparse

    formatter=optparse.TitledHelpFormatter(max_help_position=30)
    p = optparse.OptionParser(usage=usage, formatter=formatter)
    p.add_option("-q", "--quiet",   action="store_true", help="Minimal output")
    p.add_option("-v", "--verbose", action="store_true", help="Verbose output")
    p.add_option("-i", "--immediate", action="store_true", help="Immediate feedback about exceptions")
    p.add_option("--vassert", action="store_true", help="Verbalize the assert calls")
    p.add_option("--regex", help="Filtering regular expression")
    p.add_option("--xml", metavar="FILE", help="output results in XML")
    p.add_option("--html", metavar="FILE", help="output results in HTML")
    p.add_option("--color", action="store_true", help="Color output")
    p.add_option("--interval", type="float", default=0, help="Add interval between tests")
    p.add_option("--debug", action="store_true", help="Run pdb on tests that fail on Error")
    p.add_option("--threads", type="int", help="Run in a threadpool")
    p.add_option("--processes", type="int", help="Run in multiple processes")

    return p

def _get_verbosity(options):
    if options.quiet: return 0
    if options.vassert: return 3
    if options.verbose: return 2
    return 1

def _get_suites(suite, defaultTest, test_names):
    if suite is not None:
        # an explicit suite always wins
        return [suite]

    from unittest import TestLoader
    import __main__
    if len(test_names) == 0 and defaultTest is None:
        # load all tests from __main__
        return TestLoader().loadTestsFromModule(__main__)

    if len(test_names) == 0:
        test_names = [defaultTest]
    return TestLoader().loadTestsFromNames(test_names, __main__)

def _main(suite, defaultTest, options, test_names, parser):

    def require_modules(option, *modules):
        missing_modules = []
        for modulename in modules:
            try:
                __import__(modulename)
            except ImportError:
                missing_modules.append(modulename)
        if missing_modules:
            parser.error("option '%(option)s' requires missing modules "
                         "%(missing_modules)s" % vars())

    kwargs = {
        "suites" : _get_suites(suite, defaultTest, test_names),
        "verbosity" : _get_verbosity(options),
        "immediate" : options.immediate,
        "reporters" : [],
        "interval" : options.interval
    }

    if options.regex is not None:
        from extracting import regex_extractor
        kwargs["test_extractor"]  = regex_extractor(options.regex)

    if options.xml is not None:
        from reporting import XMLFileReporter
        kwargs["reporters"].append( XMLFileReporter(filename=options.xml) )
    
    if options.html is not None:
        require_modules("--html", "Ft.Xml")
        from reporting import HTMLReporter
        kwargs["reporters"].append( HTMLReporter(filename=options.html) )
    
    if options.color is not None:
        from reporting import ColoredTextReporter
        kwargs["reporter_class"] = ColoredTextReporter

    if options.debug is not None:
        import pdb
        def runDebug(test, err, flavour, reporter, real_add):
            assert flavour in ["error", "failure"]
            real_add(test, err)
            print "\nDebugging for", flavour, "in test:", \
                  reporter.getDescription(test)
            pdb.post_mortem(err[2])
        kwargs["runDebug"] = runDebug

    if options.threads is not None:
        require_modules("--threads", "twisted.python.threadpool")
        from running import ThreadedRunner
        kwargs["runner"] = ThreadedRunner(max_threads = options.threads)

    if options.processes is not None:
        from running import ProcessedRunner
        from sys import platform
        if kwargs.has_key("runDebug"):
            del kwargs["runDebug"]
            print " -- WARNING: Processed running does not support --debug yet."
            print
        if platform == "win32":
            require_modules("--processes", "Posix operation system")
        kwargs["runner"] = ProcessedRunner(max_processes = options.processes)

    import running
    running.text_run(**kwargs)

def main(suite=None, defaultTest=None):
    usage="""%prog [options] [test1 [test2 [...]]]

examples:
  %prog                          - run default set of tests
  %prog MyTestSuite              - run suite 'MyTestSuite'
  %prog MyTestCase.testSomething - run MyTestCase.testSomething
  %prog MyTestCase               - run all 'test*' test methods in MyTestCase"""

    parser = _arg_parser(usage)
    options, test_names = parser.parse_args()

    _main(suite, defaultTest, options, test_names, parser)

