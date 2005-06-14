import unittest

class RunLog:
    def __init__(self):
        self.clear()
    def clear(self):
        self.started = []
        self.successes = []
        self.errors = []
        self.failures = []
        self.finished = []
        self.stdout = ""
        self.stderr = ""

run_log = RunLog()

def logged_run(name, func, *args, **kwargs):
    run_log.started.append(name)

    try:
        func(*args, **kwargs)
        run_log.successes.append(name)
    finally:
        run_log.finished.append(name)


class CaseLetters(unittest.TestCase):
    def testA(self): logged_run("testA", self.assertEquals, "A" + "A", "AA")
    def testB(self): logged_run("testB", self.assertEquals, "B" + "B", "BB")
    def testC(self): logged_run("testC", self.assertEquals, "C" + "C", "CC")
    def testD(self): logged_run("testD", self.assertEquals, "D" + "D", "DD")
    def testE(self): logged_run("testE", self.assertEquals, "E" + "E", "EE")
    def testF(self): logged_run("testF", self.assertEquals, "F" + "F", "FF")
    def testG(self): logged_run("testG", self.assertEquals, "G" + "G", "GG")
    def testH(self): logged_run("testH", self.assertEquals, "H" + "H", "HH")
    def testI(self): logged_run("testI", self.assertEquals, "I" + "I", "II")
    def testJ(self): logged_run("testJ", self.assertEquals, "J" + "J", "JJ")
    def testK(self): logged_run("testK", self.assertEquals, "K" + "K", "KK")
    def testL(self): logged_run("testL", self.assertEquals, "L" + "L", "LL")
    def testM(self): logged_run("testM", self.assertEquals, "M" + "M", "MM")
    def testN(self): logged_run("testN", self.assertEquals, "N" + "N", "NN")
    def testO(self): logged_run("testO", self.assertEquals, "O" + "O", "OO")
    def testP(self): logged_run("testP", self.assertEquals, "P" + "P", "PP")
    def testQ(self): logged_run("testQ", self.assertEquals, "Q" + "Q", "QQ")
    def testR(self): logged_run("testR", self.assertEquals, "R" + "R", "RR")
    def testS(self): logged_run("testS", self.assertEquals, "S" + "S", "SS")
    def testT(self): logged_run("testT", self.assertEquals, "T" + "T", "TT")
    def testU(self): logged_run("testU", self.assertEquals, "U" + "U", "UU")
    def testV(self): logged_run("testV", self.assertEquals, "V" + "V", "VV")
    def testW(self): logged_run("testW", self.assertEquals, "W" + "W", "WW")
    def testX(self): logged_run("testX", self.assertEquals, "X" + "X", "XX")
    def testY(self): logged_run("testY", self.assertEquals, "Y" + "Y", "YY")
    def testZ(self): logged_run("testZ", self.assertEquals, "Z" + "Z", "ZZ")

class CaseDigits(unittest.TestCase):
    def test0(self): logged_run("test0", self.assertEquals, "0" + "0", "00")
    def test1(self): logged_run("test1", self.assertEquals, "1" + "1", "11")
    def test2(self): logged_run("test2", self.assertEquals, "2" + "2", "22")
    def test3(self): logged_run("test3", self.assertEquals, "3" + "3", "33")
    def test4(self): logged_run("test4", self.assertEquals, "4" + "4", "44")
    def test5(self): logged_run("test5", self.assertEquals, "5" + "5", "55")
    def test6(self): logged_run("test6", self.assertEquals, "6" + "6", "66")
    def test7(self): logged_run("test7", self.assertEquals, "7" + "7", "77")
    def test8(self): logged_run("test8", self.assertEquals, "8" + "8", "88")
    def test9(self): logged_run("test9", self.assertEquals, "9" + "9", "99")

class CaseMixed(unittest.TestCase):
    def testSuccess(self): logged_run("testSuccess", lambda:None)
    def testFailure(self): logged_run("testFailure", self.fail)
    def testError(self):
        def error(): raise RuntimeError
        logged_run("testError", error)
    @staticmethod
    def suite():
        return unittest.makeSuite(CaseMixed)

class CaseFailure(unittest.TestCase):
    def testFailure(self): logged_run("testFailure", self.fail)
    @staticmethod
    def suite():
        return unittest.makeSuite(CaseFailure)

class CaseError(unittest.TestCase):
    def testError(self):
        def error(): raise RuntimeError
        logged_run("testError", error)
    @staticmethod
    def suite():
        return unittest.makeSuite(CaseError)

import string
all_test_names = ["test%s" % x for x in string.uppercase + string.digits]

def suite():
    result = unittest.TestSuite()
    result.addTest( unittest.makeSuite(CaseLetters) )
    result.addTest( unittest.makeSuite(CaseDigits) )
    return result
