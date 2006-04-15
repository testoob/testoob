"""
Run all tests
"""

test_modules = [
    'small.suite',
    'medium.suite',
    'large.suite',
]

def suite():
    import unittest
    return unittest.TestLoader().loadTestsFromNames(test_modules)

if __name__ == "__main__":
    import testoob
    testoob.main(defaultTest="suite")
