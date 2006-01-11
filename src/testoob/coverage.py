# TestOOB, Python Testing Out Of (The) Box
# Copyright (C) 2005 The TestOOB Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"Code coverage module"

import trace, os, sys

class Coverage:
    """
    Python code coverage module built specifically for checking code coverage
    in tests performed by TestOOB.

    NOTE: This class uses the 'trace' module, so it may collide with anything
    else that uses 'trace' (such as debugging)
    """
    def __init__(self, ignoredirs=()):
        """
        initialize the code coverage module, gets list of directories of files
        which's coverage is not needed.
        """
        # self._covered_lines is dictionary mapping filenames to lines called.
        self._covered_lines = {}
        self._dirs_not_covered = ignoredirs

    def runfunc(self, func, *args, **kwargs):
        "Gets a function and it's arguments to run and perform code coverage test"
        sys.settrace(self._tracer)
        try:
            return func(*args, **kwargs)
        finally:
            sys.settrace(None)

    def getstatistics(self):
        """
        Returns a dictionary of statistics. the dictionary maps between a filename
        and the statistics associated to it.

        The statistics dictionary has 3 keys:
            lines   - the number of executable lines in the file
            covered - the number of lines covered in the file
            percent - the percentage of covered lines.

        This dictionary also has a special "file" (key) called '__total__', which
        holds the statistics for all the files together.
        """
        statistics = {
            "__total__": {
                "lines"  : 0,
                "covered": 0,
                "percent": 0,
            }
        }

        for filename, coverage in self.getcoverage().items():
            statistics[filename] = {
                "lines"  : len(coverage["lines"]),
                "covered": len(coverage["covered"]),
                "percent": int(100 * len(coverage["covered"]) / len(coverage["lines"]))
            }
            statistics["__total__"]["lines"]   += statistics[filename]["lines"]
            statistics["__total__"]["covered"] += statistics[filename]["covered"]

        statistics["__total__"]["percent"] = int(
            100 * statistics["__total__"]["covered"] / statistics["__total__"]["lines"])

        return statistics

    # TODO: suggested replacement for '__total__' key in getstatistics() retval
    # TODO: above. Either remove __total__, or remove these methods.
    def _sum_coverage(self, callable):
        "Helper method for _total_{lines,covered}"
        return sum([callable(coverage)
                    for coverage in self.getcoverage().values()])
    def _total_lines(self):
        return self._sum_coverage(lambda coverage: len(coverage["lines"]))
    def _total_lines_covered(self):
        return self._sum_coverage(lambda coverage: len(coverage["covered"]))
    def _total_coverage_percentage(self):
        return int(100 * self._total_covered() / self._total_lines())
    
    def getcoverage(self):
        """
        Returns a dictionary of covered lines. The dictionary maps filenames to
        another dictionary with the following keys:
            lines   - a set of number of executable lines in the file.
            covered - a set of numbers of executed lines in the file.
        """
        coverage = {}
        for filename, lines in self._covered_lines.items():
            coverage[filename] = {
                "lines"  : set(trace.find_executable_linenos(filename)),
                "covered": lines
            }
        return coverage
    
    def _should_check_file(self, filename):
        "Should we check coverage for this file?"
        for dir in self._dirs_not_covered:
            if filename.startswith(dir):
                return False
        return True
    
    def _tracer(self, frame, why, arg):
        "Trace function to be put as input for sys.settrace()"
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno

        if self._should_check_file(filename):
            self._covered_lines.setdefault(filename, set())
            self._covered_lines[filename].add(lineno)

        return self._tracer

