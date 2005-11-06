def trace():
    import sys, os
    calling_function_name = sys._getframe(1).f_code.co_name
    print "pid=%s, %r" % (os.getpid(), calling_function_name)
    
import unittest
class BlaTest(unittest.TestCase):
    def testA(self): trace()
    def testB(self): trace()
    def testC(self): trace()
    def testD(self): trace()
    def testE(self): trace()
    def testF(self): trace()
    def testG(self): trace()
    def testH(self): trace()
    def testI(self): trace()
    def testJ(self): trace()
    def testK(self): trace()
    def testL(self): trace()
    def testM(self): trace()
    def testN(self): trace()
    def testO(self): trace()
    def testP(self): trace()
    def testQ(self): trace()

def suite():
	return unittest.makeSuite(BlaTest)
    
if __name__ == "__main__":
    unittest.main()
