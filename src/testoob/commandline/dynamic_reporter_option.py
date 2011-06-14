import parsing
parsing.parser.add_option("--add_reporter", metavar="CLASS",
    help="dynamically load reporter (my_package.my_module.my_reporter_class, must be in the PYTHONPATH)")

def split_module_classname(classname):
    last_dot = classname.rfind(".")
    module_name = classname[:last_dot]
    class_name = classname[last_dot+1:]
    return module_name, class_name

def dynamically_import_class(classname):
    module_name, class_name = split_module_classname(classname)

    try:
        module = __import__(module_name, globals(), locals(), [class_name])
        return getattr(module, class_name)
    except:
        raise parsing.ArgumentsError("Unable to load or find class '%s'" % classname)

def process_options(options):
    if options.add_reporter is None:
        return

    reporter_classname = options.add_reporter

    klass = dynamically_import_class(reporter_classname)

    from testoob.reporting.base import IReporter
    if not issubclass(klass, IReporter):
        raise parsing.ArgumentsError("class '%s' must subclass testoob.reporting.base.IReporter" % reporter_classname)

    # instantiate the klass and attach it as a reporter
    parsing.kwargs["reporters"].append( klass() )

parsing.option_processors.append(process_options)
