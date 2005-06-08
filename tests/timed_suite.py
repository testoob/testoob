import unittest, time, random

class StateSensitiveTestCase(unittest.TestCase):
    def setUp(self):
        self.l = []
    def tearDown(self):
        del self.l

    def testOne(self):
        self.assertEqual([], self.l)
        self.l.append(1)
        time.sleep(1)
        self.assertEqual([1], self.l)
        self.l.append("One")
        time.sleep(1)
        self.assertEqual([1, "One"], self.l)

    def testTwo(self):
        self.assertEqual([], self.l)
        self.l.append(2)
        time.sleep(1)
        self.assertEqual([2], self.l)
        self.l.append("Two")
        time.sleep(1)
        self.assertEqual([2, "Two"], self.l)

def _hashed_float(s):
    """returns a float in the range [0, 1) based on a hash of the string.
    A given string will always return the same value, but different strings
    will return very different values."""
    import md5, struct
    [number] = struct.unpack("<H", md5.new(s).digest()[:2])
    return number / float(0xFFFF)

class SleepingTestCase(unittest.TestCase):
    def sleep(self, name, max_seconds=2):
        # basing the sleep time on _hashed_float(name) causes different tests
        # to sleep different amounts, but each test will sleep the same amount
        # across test runs.
        sleep_time = _hashed_float(name) * max_seconds
        time.sleep(sleep_time)

    def testA(self): self.sleep("testA")
    def testB(self): self.sleep("testB")
    def testC(self): self.sleep("testC")
    def testD(self): self.sleep("testD")
    def testE(self): self.sleep("testE")
    def testF(self): self.sleep("testF")
    def testG(self): self.sleep("testG")
    def testH(self): self.sleep("testH")
    def testI(self): self.sleep("testI")
    def testJ(self): self.sleep("testJ")
    def testK(self): self.sleep("testK")
    def testThis(self): self.sleep("testThis")
    def testThat(self): self.sleep("testThat")

def suite():
    tests = [StateSensitiveTestCase, SleepingTestCase]
    return unittest.TestSuite(map(unittest.makeSuite,tests))

if __name__ == "__main__":
    import testoob
    testoob.main()
