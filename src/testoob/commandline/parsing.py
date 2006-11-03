class ArgumentsError(Exception): pass

def require_modules(option, *modules):
    assert len(modules) > 0
    missing_modules = []
    for modulename in modules:
        try:
            __import__(modulename)
        except ImportError:
            missing_modules.append(modulename)
    if missing_modules:
        raise ArgumentsError(
                "option '%(option)s' requires missing modules "
                "%(missing_modules)s" % vars())

def require_posix(option):
    try:
        import posix
    except ImportError:
        raise ArgumentsError("option '%s' requires a POSIX environment" % option)

def _parser():
    usage="""%prog [options] [test1 [test2 [...]]]

examples:
  %prog                          - run default set of tests
  %prog MyTestSuite              - run suite 'MyTestSuite'
  %prog MyTestCase.testSomething - run MyTestCase.testSomething
  %prog MyTestCase               - run all 'test*' test methods in MyTestCase"""

    try:
        import optparse
    except ImportError:
        from testoob.compatibility import optparse

    formatter=optparse.TitledHelpFormatter(max_help_position=30)
    from testoob import __version__ as version
    return optparse.OptionParser(
            usage = usage,
            formatter = formatter,
            version = "Testoob %s" % version,
        )

parser = _parser()

option_processors = []
