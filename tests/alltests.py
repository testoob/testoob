"""
Run all tests
"""

test_modules = [
    'other.runningtests',
    'other.extractingtests',
    'system.systemtests',
    'unit.test_testing',
    'unit.test_threadpool',
    'unit.test_coverage',
]

def suite():
    import unittest
    return unittest.TestLoader().loadTestsFromNames(test_modules)

if __name__ == "__main__":
    import testoob
    testoob.main(defaultTest="suite")
