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

def choose_decorator(profiler_name):
    if profiler_name == "hotshot":
        return hotshot_decorator
    if profiler_name == "profile":
        return profile_decorator
    assert False # should never reach here

def hotshot_decorator(filename):
    def decorator(callable):
        def wrapper(*args, **kwargs):
            import hotshot
            prof = hotshot.Profile(filename)
            try:
                return prof.runcall(callable, *args, **kwargs)
            finally:
                prof.close()
                from hotshot import stats
                try:
                    stats.load(filename).sort_stats("time").print_stats()
                except hotshot.ProfilerError:
                    raise IOError("Error reading stats from '%s', file may be corrupt" % filename)

        return wrapper
    return decorator

def profile_decorator(filename):
    def decorator(callable):
        def wrapper(*args, **kwargs):
            result = []
            def run_callable():
                """
                A local function we can refer to in a tring with profile.run.
                Calls the callable, and saves the result in the 'result' list.
                """
                assert len(result) == 0
                result.append( callable(*args, **kwargs) )

            import profile

            try: from cProfile import Profile
            except ImportError: from profile import Profile
            p = profile.Profile()

            # passing the environment so the code is run in the current context
            p = p.runctx("run_callable()", globals(), locals())

            p.dump_stats(filename)
            p.print_stats(sort="time")

            assert len(result) == 1
            return result[0]
        return wrapper
    return decorator

