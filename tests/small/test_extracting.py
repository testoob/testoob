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

def sample_suite():
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

def apply_decorator(decorator, iterable):
    "This isn't trivial, maybe should be made trivial?"
    # The decorator decorates the extractor, in this case we use the 'trivial'
    # extractor "iter"
    extractor = iter
    return decorator(extractor)(iterable)
    
class unit_tests(unittest.TestCase):
    "Small-grain tests for testoob.extracting"
    def testFullExtractor(self):
        extractor = extracting.full_extractor( sample_suite() )
        actual = set([test.id().split('.')[-1] for test in extractor])
        self.assertEqual(set(('testFoo', 'testBar', 'testBaz')), actual)

    def testPredicate(self):
        decorator = extracting.predicate(lambda x:x>5)
        iterator = apply_decorator(decorator, [7,2,5,6])
        self.assertEqual([7,6], list(iterator))

if __name__ == "__main__":
    import testoob
    testoob.main()
