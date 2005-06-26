from __future__ import generators # Python 2.2 friendly

import unittest
from types import ModuleType

import runningtests
import extractingtests
import systemtests

def imported_test_modules():
    for val in globals().values():
        if type(val) == ModuleType and \
           hasattr(val, "suite") and \
           callable(val.suite):
               yield val

def suite():
    result = unittest.TestSuite()
    for module in imported_test_modules():
        result.addTest(module.suite())
    return result

if __name__ == "__main__": unittest.main(defaultTest="suite")
