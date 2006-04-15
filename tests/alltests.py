"""
Run all tests
"""

test_modules = [
    'medium.test_running',
    'medium.test_extracting',
    'large.systemtests',
    'small.test_testing',
    'small.test_threadpool',
    'small.test_coverage',
]

def suite():
    import unittest
    return unittest.TestLoader().loadTestsFromNames(test_modules)

if __name__ == "__main__":
    import testoob
    testoob.main(defaultTest="suite")
