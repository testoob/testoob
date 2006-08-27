"extracting unit tests"

import unittest
from testoob import extracting

try:
    set
except NameError:
    # Python 2.3 or older
    try:
        from sets import Set as set
    except ImportError:
        # Python 2.2 or older
        from compatibility.sets import Set as set

def _sample_suite():
    # inside a function, so it won't be found by the collection code
    class Test1(unittest.TestCase):
        def testFoo(self): pass
        def testBar(self): pass
    class Test2(unittest.TestCase):
        def testBaz(self): pass
    result = unittest.TestSuite()
    result.addTest(unittest.makeSuite(Test1))
    result.addTest(unittest.makeSuite(Test2))
    return result

def _test_basenames(tests):
    return set([test.id().split('.')[-1] for test in tests])

class unit_tests(unittest.TestCase):
    "Small-grain tests for testoob.extracting"
    def setUp(self):
        self.all_tests = extracting.full_extractor( _sample_suite() )
    def tearDown(self):
        del self.all_tests

    def testFullExtractor(self):
        actual = _test_basenames(self.all_tests)
        self.assertEqual(set(('testFoo', 'testBar', 'testBaz')), actual)

    def testPredicate(self):
        decorator = extracting.predicate(lambda x:x>5)
        iterator = decorator(iter)([7,2,5,6])
        self.assertEqual([7,6], list(iterator))

    def testRegex(self):
        decorator = extracting.regex(r"te.*(Bar$|F)")
        extractor = decorator(extracting.full_extractor)
        tests = extractor( _sample_suite() )
        self.assertEqual(set(('testFoo', 'testBar')), _test_basenames(tests))
        

if __name__ == "__main__":
    import testoob
    testoob.main()
