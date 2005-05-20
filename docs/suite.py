import unittest
class MyTestCase(unittest.TestCase):
  def setUp(self):   pass
  def testFoo(self): pass
  def testBar(self): self.fail('bla')
  def testBaz(self): pass

if __name__ == "__main__":
  import testoob
  testoob.main()
