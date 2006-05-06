# Testoob, Python Testing Out Of (The) Box
# Copyright (C) 2005-2006 The Testoob Team
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

"Profiling support code"

MAX_PROFILING_LINES_TO_PRINT = 30

def _helper_class(profiler_name):
    if profiler_name == "hotshot":
        return HotshotHelper
    if profiler_name == "profile":
        return ProfileHelper
    assert False # should never reach here

def profiling_decorator(profiler_name, filename):
    def decorator(callable):
        def wrapper(*args, **kwargs):
            helper = _helper_class(profiler_name)(filename, callable, *args, **kwargs)
            print "Profiling information saved to file '%s'" % helper.filename
            helper.run()
            helper.print_stats(MAX_PROFILING_LINES_TO_PRINT)

            return helper.result
        return wrapper
    return decorator

class ProfilingHelper(object):
    def __init__(self, filename, callable, *args, **kwargs):
        self.filename = filename
        self.callable = callable
        self.args = args
        self.kwargs = kwargs

        self.result = None

    def print_stats(self, *args):
        self.stats().sort_stats("time").print_stats(*args)

    def run(self):
        raise NotImplementedError

    def stats(self):
        raise NotImplementedError

class HotshotHelper(ProfilingHelper):
    def run(self):
        import hotshot
        p = hotshot.Profile(self.filename)
        try:
            self.result = p.runcall(self.callable, *self.args, **self.kwargs)
        finally:
            p.close()

    def stats(self):
        from hotshot import stats
        try:
            return stats.load(self.filename)
        except hotshot.ProfilerError:
            raise IOError("Error reading stats from '%s', file may be corrupt" % filename)

class ProfileHelper(ProfilingHelper):
    def run(self):
        def run_callable():
            "A local function we can refer to in a string with profile.run"
            self.result = self.callable(*self.args, **self.kwargs)

        try:
            from cProfile import Profile
        except ImportError:
            from profile import Profile

        self.p = Profile().runctx("run_callable()", globals(), locals())
        self.p.dump_stats(self.filename)

    def stats(self):
        import pstats
        return pstats.Stats(self.p)
