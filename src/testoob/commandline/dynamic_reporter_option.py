import parsing
parsing.parser.add_option("--add_reporter", metavar="CLASSNAME",
    help="dynamically load reporter class (package.module.classname), "
         "must be in the PYTHONPATH")

def split_module_classname(full_class_name):
    last_dot = full_class_name.rfind(".")
    module_name = full_class_name[:last_dot]
    class_name = full_class_name[last_dot+1:]
    return module_name, class_name

def dynamically_import_class(full_class_name):
    module_name, class_name = split_module_classname(full_class_name)

    try:
        module = __import__(module_name, globals(), locals(), [class_name])
        return getattr(module, class_name)
    except ImportError, e:
        # TODO: show entire stack trace?
        raise parsing.ArgumentsError("Can't load module '%s', got error: %s" % (module_name, e))
    except AttributeError:
        raise parsing.ArgumentsError("Can't find class '%s' in module '%s'" % (class_name, module_name))

def process_options(options):
    if options.add_reporter is None:
        return

    klass = dynamically_import_class(options.add_reporter)

    from testoob.reporting.base import IReporter
    if not issubclass(klass, IReporter):
        raise parsing.ArgumentsError("class '%s' must subclass testoob.reporting.base.IReporter" % options.add_reporter)

    # instantiate the klass and attach it as a reporter
    parsing.kwargs["reporters"].append( klass() )

parsing.option_processors.append(process_options)
