import unittest
class CaseLetters(unittest.TestCase):
    def testA(self):
        self.assertEqual(1, 1)
    def testB(self):
        self.assertFalse(False)

class CaseDigits(unittest.TestCase):
    def test1(self):
        self.failUnless("One" != "Two")
    def test2(self):
        self.failIf("Three" != "Three")

if __name__ == "__main__":
    import testoob
    testoob.main()
