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

import os, sys, trace

try:
    sum
except NameError:
    # Python 2.2 compatibility
    import operator
    sum = lambda seq: reduce(operator.add, seq)

try:
    set
except NameError:
    # Python 2.3 compatibility
    from sets import Set as set
except ImportError:
    # Python 2.2. compatibility
    from compatibility.sets import Set as set

class Coverage:
    """
    Python code coverage module built specifically for checking code coverage
    in tests performed by TestOOB.

    NOTE: This class depends on the 'trace' module.
    """
    def __init__(self, ignorepaths=()):
        """
        initialize the code coverage module, gets list of directories and files
        which's coverage is not needed.
        """
        # coverage is a dictinary mapping filenames to another dictionary with
        # the following keys:
        #    lines   - a set of number of executable lines in the file.
        #    covered - a set of numbers of executed lines in the file.
        self.coverage = {}
        self.ignorepaths = map(os.path.abspath, ignorepaths)
        self.modname = trace.modname

    def runfunc(self, func, *args, **kwargs):
        "Gets a function and it's arguments to run and perform code coverage test"
        sys.settrace(self._tracer)
        try:
            return func(*args, **kwargs)
        finally:
            sys.settrace(None)

    def getstatistics(self):
        """
        Returns a dictionary of statistics. the dictionary maps between a
        filename and the statistics associated to it.

        The statistics dictionary has 3 keys:
            lines   - the number of executable lines in the file
            covered - the number of lines covered in the file
            percent - the percentage of covered lines.

        This dictionary also has a special "file" (key) called '__total__',
        which holds the statistics for all the files together.
        """
        statistics = {}
        for filename, coverage in self.coverage.items():
            statistics[filename] = self._single_file_statistics(coverage)
        return statistics

    def _single_file_statistics(self, coverage_dict):
        def num_lines(): return len(coverage_dict["lines"])
        def num_lines_covered(): return len(coverage_dict["covered"])
        def percentage():
            if num_lines() > 0:
                return int(100 * num_lines_covered()) / num_lines()
            else:
                return 0
        return {
            "lines"  : num_lines(),
            "covered": num_lines_covered(),
            "percent": percentage(),
        }


    def _sum_coverage(self, callable):
        "Helper method for _total_{lines,covered}"
        return sum([callable(coverage)
                    for coverage in self.coverage.values()])
    def total_lines(self):
        return self._sum_coverage(lambda coverage: len(coverage["lines"]))
    def total_lines_covered(self):
        return self._sum_coverage(lambda coverage: len(coverage["covered"]))
    def total_coverage_percentage(self):
        if self.total_lines() == 0:
            return 0
        return int(100 * self.total_lines_covered() / self.total_lines())

    def _should_cover_frame(self, frame):
        "Should we check coverage for this file?"
        filename = os.path.abspath(frame.f_code.co_filename)
        lineno = frame.f_lineno
        for path in self.ignorepaths:
            if (filename).startswith(path):
                return False
        
        if not self.coverage.has_key(filename):
            self.coverage[filename] = {
                "lines": set(trace.find_executable_linenos(filename)),
                "covered": set()
            }
        return lineno in self.coverage[filename]["lines"]
    
    def _tracer(self, frame, why, arg):
        "Trace function to be put as input for sys.settrace()"
        if self._should_cover_frame(frame):
            filename = os.path.abspath(frame.f_code.co_filename)
            lineno = frame.f_lineno
            self.coverage[filename]["covered"].add(lineno)

        return self._tracer

