import sys

class Capabilities(object):
    @property
    def getframe(self):
        try:
            sys._getframe()
            return True
        except ValueError:
            # IronPython 1.1
            return False

    @property
    def f_back(self):
        return self.getframe and hasattr(sys._getframe(), "f_back")

    @property
    def settrace(self):
        try:
            sys.settrace(None)
            return True
        except NotImplementedError:
            return False

c = Capabilities()
