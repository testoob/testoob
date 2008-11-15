import sys

class Capabilities(object):
    @property
    def f_back(self):
        return hasattr(sys._getframe(), "f_back")

    @property
    def settrace(self):
        try:
            sys.settrace(None)
            return True
        except NotImplementedError:
            return False

c = Capabilities()
