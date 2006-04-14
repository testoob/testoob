"""
Run all tests
"""

test_modules = [
    'runningtests',
    'extractingtests',
    'systemtests',
    'unit.testing_unittest',
    'unit.test_threadpool',
]

def suite():
    import unittest
    return unittest.TestLoader().loadTestsFromNames(test_modules)

if __name__ == "__main__":
    import testoob
    testoob.main(defaultTest="suite")
