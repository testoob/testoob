import parsing
parsing.parser.add_option("--add_reporter", metavar="CLASS", help="dynamically load reporter (my_package.my_module.my_reporter_class, must be in the PYTHONPATH)")

def process_options(options):
    if options.add_reporter is None:
        return

    # split package/module from class name
    mod_class_split_loc = options.add_reporter.rfind(".")
    mod_name = options.add_reporter[0:mod_class_split_loc]
    class_name = options.add_reporter[mod_class_split_loc+1:]

    try:
        # dynamically import the module
        mod = __import__(mod_name, globals(), locals(), [class_name])
        # get the class
        klass = getattr(mod, class_name)
    except:
        # raise command line error
        from commandline.parsing import ArgumentsError
        raise ArgumentsError("Unable to load or find reporter class")

    # instantiate the class if it is derived from IReporters
    from testoob.reporting.base import IReporter
    if issubclass(klass, IReporter):
        # instantiate the klass and attach it as a reporter
        parsing.kwargs["reporters"].append( klass() )
    else:
        # raise command line error
        from commandline.parsing import ArgumentsError
        raise ArgumentsError("added reporter class must be subclass of testoob.reporting.base.IReporters")

parsing.option_processors.append(process_options)
