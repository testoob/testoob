def _parse_args():
    import optparse
    usage="""%prog [options] [test1 [test2 [...]]]

examples:
  %prog                          - run default set of tests
  %prog MyTestSuite              - run suite 'MyTestSuite'
  %prog MyTestCase.testSomething - run MyTestCase.testSomething
  %prog MyTestCase               - run all 'test*' test methods in MyTestCase"""

    formatter=optparse.TitledHelpFormatter(max_help_position=30)
    p = optparse.OptionParser(usage=usage, formatter=formatter)
    p.add_option("-q", "--quiet",   action="store_true", help="Minimal output")
    p.add_option("-v", "--verbose", action="store_true", help="Verbose output")
    p.add_option("--regex", help="Filtering regular expression")
    p.add_option("--xml", metavar="FILE", help="output results in XML")
    p.add_option("--html", metavar="FILE", help="output results in HTML")
    p.add_option("--color", action="store_true", help="Color output")
    return p.parse_args()

def _get_verbosity(options):
    if options.quiet: return 0
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

def main(suite=None, defaultTest=None):
    options, test_names = _parse_args()

    kwargs = {
        "suites" : _get_suites(suite, defaultTest, test_names),
        "verbosity" : _get_verbosity(options),
        "reporters" : [],
    }

    if options.regex is not None:
        from extractors import regex_extractor
        kwargs["test_extractor"]  = regex_extractor(options.regex)

    if options.xml is not None:
        from reporting import XMLFileReporter
        kwargs["reporters"].append( XMLFileReporter(filename=options.xml) )
    
    if options.html is not None:
        from reporting import HTMLReporter
        kwargs["reporters"].append( HTMLReporter(filename=options.html) )
    
    if options.color is not None:
        from reporting import ColoredTextReporter
        kwargs["reporter_class"] = ColoredTextReporter

    import running
    running.text_run(**kwargs)
