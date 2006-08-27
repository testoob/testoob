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

def _tests_after_decorator(decorator):
    extractor = decorator(extracting.full_extractor)
    return extractor( _sample_suite() )

def _test_basenames_after_decorator(decorator):
    return _test_basenames(_tests_after_decorator(decorator))

class unit_tests(unittest.TestCase):
    "Small-grain tests for testoob.extracting"
    def setUp(self):
        self.all_tests = extracting.full_extractor( _sample_suite() )
    def tearDown(self):
        del self.all_tests

    def testFullExtractor(self):
        # The helper already uses extracting.full_extractor
        actual = _test_basenames_after_decorator(lambda x:x)
        self.assertEqual(set(('testFoo', 'testBar', 'testBaz')), actual)

    def testPredicate(self):
        decorator = extracting.predicate(lambda x:x>5)
        iterator = decorator(iter)([7,2,5,6])
        self.assertEqual([7,6], list(iterator))

    def testRegex(self):
        decorator = extracting.regex(r"te.*(Bar$|F)")
        actual = _test_basenames_after_decorator(decorator)
        self.assertEqual(set(('testFoo', 'testBar')), actual)

    def testGlob(self):
        decorator = extracting.glob("*F*")
        actual = _test_basenames_after_decorator(decorator)
        self.assertEqual(set(('testFoo',)), actual)

    def testRepeat(self):
        decorator = extracting.repeat(3)
        iterator = decorator(iter)([9,4])
        self.assertEqual([9,9,9,4,4,4], list(iterator))

    def testRandomize(self):
        original = range(15)
        decorator = extracting.randomize()
        iterator = decorator(iter)(original)

        # This may fail. If the randomization is perfect, the probability is 1
        # in 15-factorial (about 2^(-40)), which is neglible. It isn't perfect,
        # but should be close enough.
        self.assertNotEqual(original, list(iterator))

if __name__ == "__main__":
    import testoob
    testoob.main()
