"""
Run all tests
"""

test_modules = [
    'other.test_running',
    'other.test_extracting',
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
