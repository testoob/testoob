"""
Run all tests
"""

test_modules = [
    'runningtests',
    'extractingtests',
    'systemtests',
    'testing_unittest',
]

def suite():
    import unittest
    return unittest.TestLoader().loadTestsFromNames(test_modules)

if __name__ == "__main__":
    import testoob
    testoob.main(defaultTest="suite")
