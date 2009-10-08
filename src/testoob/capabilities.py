import sys

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
    getframe = property(getframe)

    def f_back(self):
        return self.getframe and hasattr(sys._getframe(), "f_back")
    f_back = property(f_back)

    def settrace(self):
        try:
            sys.settrace(None)
            return True
        except NotImplementedError:
            return False
    settrace = property(settrace)

c = Capabilities()
