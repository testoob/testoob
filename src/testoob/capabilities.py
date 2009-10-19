import sys

def _cache_result(f):
    x = []
    def wrapper(*args, **kwargs):
        if not x: x.append(f(*args, **kwargs))
        return x[0]
    return wrapper

class Capabilities(object):
    def getframe(self):
        try:
            sys._getframe()
            return True
        except ValueError:
            # IronPython 1.1
            return False
        except AttributeError:
            # IronPython 2.6
            return False
    getframe = _cache_result(getframe)
    getframe = property(getframe)

    def f_back(self):
        return self.getframe and hasattr(sys._getframe(), "f_back")
    f_back = _cache_result(f_back)
    f_back = property(f_back)

    def settrace(self):
        try:
            sys.settrace(None)
            return True
        except NotImplementedError:
            return False
    settrace = _cache_result(settrace)
    settrace = property(settrace)

    def trace_coverage_support(self, sample_filename):
        try:
            import trace
            trace.find_executable_linenos(sample_filename)
            return True
        except NotImplementedError:
            return False
    trace_coverage_support = _cache_result(trace_coverage_support)

c = Capabilities()
