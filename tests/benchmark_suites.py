from unittest import TestCase

NUM_REPEATS=10000

class successes(TestCase):
    def test_assert_equal(self):
        for i in xrange(NUM_REPEATS):
            self.assertEqual(0, 0)

    def test_fail_if(self):
        for i in xrange(NUM_REPEATS):
            self.failIf( False )

    def test_assert_raises(self):
        def foo():
            raise RuntimeError()
        for i in xrange(NUM_REPEATS):
            self.assertRaises(RuntimeError, foo)
