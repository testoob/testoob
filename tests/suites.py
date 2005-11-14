import unittest

class CaseLetters(unittest.TestCase):
    def testA(self): self.assertEquals("A" + "A", "AA")
    def testB(self): self.assertEquals("B" + "B", "BB")
    def testC(self): self.assertEquals("C" + "C", "CC")
    def testD(self): self.assertEquals("D" + "D", "DD")
    def testE(self): self.assertEquals("E" + "E", "EE")
    def testF(self): self.assertEquals("F" + "F", "FF")
    def testG(self): self.assertEquals("G" + "G", "GG")
    def testH(self): self.assertEquals("H" + "H", "HH")
    def testI(self): self.assertEquals("I" + "I", "II")
    def testJ(self): self.assertEquals("J" + "J", "JJ")
    def testK(self): self.assertEquals("K" + "K", "KK")
    def testL(self): self.assertEquals("L" + "L", "LL")
    def testM(self): self.assertEquals("M" + "M", "MM")
    def testN(self): self.assertEquals("N" + "N", "NN")
    def testO(self): self.assertEquals("O" + "O", "OO")
    def testP(self): self.assertEquals("P" + "P", "PP")
    def testQ(self): self.assertEquals("Q" + "Q", "QQ")
    def testR(self): self.assertEquals("R" + "R", "RR")
    def testS(self): self.assertEquals("S" + "S", "SS")
    def testT(self): self.assertEquals("T" + "T", "TT")
    def testU(self): self.assertEquals("U" + "U", "UU")
    def testV(self): self.assertEquals("V" + "V", "VV")
    def testW(self): self.assertEquals("W" + "W", "WW")
    def testX(self): self.assertEquals("X" + "X", "XX")
    def testY(self): self.assertEquals("Y" + "Y", "YY")
    def testZ(self): self.assertEquals("Z" + "Z", "ZZ")

class CaseDigits(unittest.TestCase):
    def test0(self): self.assertEquals("0" + "0", "00")
    def test1(self): self.assertEquals("1" + "1", "11")
    def test2(self): self.assertEquals("2" + "2", "22")
    def test3(self): self.assertEquals("3" + "3", "33")
    def test4(self): self.assertEquals("4" + "4", "44")
    def test5(self): self.assertEquals("5" + "5", "55")
    def test6(self): self.assertEquals("6" + "6", "66")
    def test7(self): self.assertEquals("7" + "7", "77")
    def test8(self): self.assertEquals("8" + "8", "88")
    def test9(self): self.assertEquals("9" + "9", "99")

class CaseSlow(unittest.TestCase):
    def testSleep(self):
        import time
        time.sleep(2)
        self.assert_(True)
    def testBuisy(self):
        import time
        start = time.time()
        while time.time() - start < 2:
            time.sleep(1)
        self.assert_(True)

class CaseNames(unittest.TestCase):
    def testDatabaseError(self): pass
    def testDatabaseConnections(self): pass
    def testFilesystemLocal(self): pass
    def testFilesystemRemote(self): pass
    def testFilesystemError(self): pass

class CaseMixed(unittest.TestCase):
    def testSuccess(self): pass
    def testFailure(self): self.fail()
    def testError(self): raise RuntimeError

    def suite():
        return unittest.makeSuite(CaseMixed)
    suite = staticmethod(suite)

class CaseFailure(unittest.TestCase):
    def testFailure(self): self.fail()
    def suite():
        return unittest.makeSuite(CaseFailure)
    suite = staticmethod(suite)

class CaseError(unittest.TestCase):
    def testError(self): raise RuntimeError
    def suite():
        return unittest.makeSuite(CaseError)
    suite = staticmethod(suite)

class CaseEmpty(unittest.TestCase):
    def suite():
        return unittest.makeSuite(CaseEmpty)
    suite = staticmethod(suite)

class MoreTests(unittest.TestCase):
    def testAssertEqualWithFormatString(self):
        self.assertEquals("%s", "%s")

class AssertRaisesTests(unittest.TestCase):
    def rasingFunc(a,b,c):
        raise Exception("Blah!")
    def testAssertRaisesArgs(self):
        self.assertRaises(Exception, self.rasingFunc, 1, 2, 3)
    def testAssertRaisesArgsKwargs(self):
        self.assertRaises(Exception, self.rasingFunc, 1, b = 2, c = 3)
    def testAssertRaisesKwargs(self):
        self.assertRaises(Exception, self.rasingFunc, a = 1, b = 2, c = 3)
    def suite():
        return unittest.makeSuite(AssertRaisesTests)
    suite = staticmethod(suite)

class CaseDocstring(unittest.TestCase):
    def testPass(self):
        "this test always passes"
        pass

import string
all_test_names = ["test%s" % x for x in string.uppercase + string.digits]
all_asserts = {}
for test_name in all_test_names:
    all_asserts[test_name] = ("assertEquals", None.__class__)

def suite():
    result = unittest.TestSuite()
    result.addTest( unittest.makeSuite(CaseLetters) )
    result.addTest( unittest.makeSuite(CaseDigits) )
    return result
