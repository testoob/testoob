#!/usr/bin/python

import pyunitex, sample_suite, inet_suite
def suite():
    import unittest
    result = unittest.TestSuite()
    result.addTest( sample_suite.suite() )
    result.addTest( inet_suite.suite() )
    return result

if __name__ == "__main__": pyunitex.examples(suite())
