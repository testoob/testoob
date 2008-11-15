import sys

class Capabilities(object):
    @property
    def f_back(self):
        return hasattr(sys._getframe(), "f_back")

c = Capabilities()
