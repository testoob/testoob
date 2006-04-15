"Tests for the dummy project"

import dummyproject
import unittest

class DummyProjectTests(unittest.TestCase):
    def testDoThings(self):
        self.assertEqual(5, dummyproject.do_things(False))
    def testDoMoreThings(self):
        self.assertEqual(6, dummyproject.do_more_things())
