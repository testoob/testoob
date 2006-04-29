from unittest import TestCase
import missing_eol

class missing_eol_tests(TestCase):
    def test_foo(self):
        self.assertEqual(6, missing_eol.foo(3))
    def test_bar(self):
        self.assertEqual("", missing_eol.bar())
