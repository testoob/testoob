import unittest

class CommandLineTestCase(unittest.TestCase):
    pass

def suite(): return unittest.makeSuite(CommandLineTestCase)
if __name__ == "__main__": unittest.main()
