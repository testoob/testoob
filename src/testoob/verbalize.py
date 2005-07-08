def _import(package_name, class_name):
    return getattr(__import__(package_name), class_name)

def _create_message(method_name, variables_names, variables_values):
    msg = "[ %s (" + method_name + ") "
    for i in xrange(len(variables_values)):
        msg += variables_names[i] + ": \"" + str(variables_values[i]) + "\" "
    return msg + "]"

def _make_method_verbose(Class, method_name, reporter):
    variables = eval("Class.%s" % method_name).func_code.co_varnames
    setattr(Class, "_real_function_%s" % method_name, eval("Class.%s" % method_name))
    method = eval("Class._real_function_%s" % method_name)
    def _new_func(*args):
        msg = _create_message(method_name, variables[1:], args[1:])
        try:
            method(*args)
        except:
            reporter.addVassert(msg, '-')
            raise
        reporter.addVassert(msg, '+')

    setattr(Class, method_name, _new_func)

def make_methods_verbose(module_name, class_name, methods_pattern, reporter):
    Class = _import(module_name, class_name)
    from re import match
    for method_name in dir(Class):
        if match(methods_pattern, method_name):
            _make_method_verbose(Class, method_name, reporter)

