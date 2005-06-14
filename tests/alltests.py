import unittest
from types import ModuleType

import runningtests
import extractingtests

def suite():
    result = unittest.TestSuite()

    [
        result.addTest(val.suite())

        for val in globals().values()

        if type(val) == ModuleType and
           hasattr(val, "suite") and
           callable(val.suite)
    ]

    return result

if __name__ == "__main__": unittest.main(defaultTest="suite")
