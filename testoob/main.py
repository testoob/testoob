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
    p.add_option("-r", "--regex", help="Filtering regular expression")
    return p.parse_args()

def main():
    options, args = _parse_args()

    verbosity = 1
    if options.quiet: verbosity = 0
    if options.verbose: verbosity = 2

    from unittest import TestLoader
    import __main__
    if len(args) == 0:
        suites = TestLoader().loadTestsFromModule(__main__)
    else:
        suites = TestLoader().loadTestsFromNames(args, __main__)

    kwargs = {}
    kwargs["verbosity"] = verbosity
    if options.regex is not None:
        from extractors import regex_extractor
        kwargs["test_extractor"]  = regex_extractor(options.regex)

    import running
    running.text_run(suites=suites, **kwargs)
