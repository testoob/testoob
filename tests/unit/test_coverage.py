"coverage tests"

from testoob import coverage
from unittest import TestCase

import coverage_sample_module as sample

class CoverageTest(TestCase):
    def setUp(self):
        self.coverage = coverage.Coverage()
    def tearDown(self):
        del self.coverage

class unit_tests(CoverageTest):
    "Small-grain tests for Coverage"

    sample_coverage_dictionary = {
        "one.py" : { "lines"   : range(100),
                     "covered" : range(30,100) },
        "two.py" : { "lines"   : range(66),
                     "covered" : range(66) },
    }

    def test_total_lines(self):
        self.coverage.coverage = self.sample_coverage_dictionary.copy()
        self.assertEqual( 166, self.coverage.total_lines() )

    def test_total_lines_covered(self):
        self.coverage.coverage = self.sample_coverage_dictionary.copy()
        self.assertEqual( 136, self.coverage.total_lines_covered() )

    def test_total_coverage_percentage(self):
        self.coverage.coverage = self.sample_coverage_dictionary.copy()
        self.assertEqual( 81, self.coverage.total_coverage_percentage() )

class system_tests(CoverageTest):
    "Large-grain tests for Coverage"

    def test_percentage_full(self):
        self.coverage.runfunc(sample.foo, 5)
        self.assertEqual( 100, self.coverage.total_coverage_percentage() )

if __name__ == "__main__":
    testoob.main()
