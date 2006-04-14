"coverage unit tests"

from testoob import coverage
from unittest import TestCase

import coverage_sample_module as sample

class tests(TestCase):
    def test_percentage_full(self):
        c = coverage.Coverage()
        c.runfunc(sample.foo, 5)
        self.assertEqual( 100, c.total_coverage_percentage() )

if __name__ == "__main__":
    testoob.main()
