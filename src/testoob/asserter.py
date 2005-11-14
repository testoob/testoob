# TestOOB, Python Testing Out Of (The) Box
# Copyright (C) 2005 Ori Peleg, Barak Schiller, and Misha Seltzer
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

class Asserter:
    # Singleton
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state
        # initialize _reporter only if it's the first time the ctor is called.
        if not self.__shared_state:
            self._reporters = {}

    def _import(self, package_name, class_name):
        return getattr(__import__(package_name), class_name)

    def _make_assert_report(self, Class, method_name):
        # Prevent recursion (accures in testoob tests, when ran with testoob :-) ).
        if getattr(Class, method_name).im_func.__name__ == "_assert_reporting_func":
            return
        variables = eval("Class.%s" % method_name).func_code.co_varnames
        setattr(Class, "_real_function_%s" % method_name, eval("Class.%s" % method_name))
        method = eval("Class._real_function_%s" % method_name)
        def _assert_reporting_func(*args, **kwargs):
            num_free_args = len(variables)
            additional_args = ()
            if kwargs:
                num_free_args -= 1
                additional_args = (kwargs,)
            if len(args) > num_free_args:
                num_free_args -= 1
                additional_args = args[num_free_args:] + additional_args
            # Can't be a dictionary, because the order matters.
            varList = zip(variables[1:], (args[1:num_free_args] + additional_args))
            test = args[0]
            # If we run something that has no reporter, it should just run
            # (happens in testing of testoob with testoob).
            if not self._reporters.get(test):
                return method(*args, **kwargs)
            try:
                method(*args, **kwargs)
            except Exception, e:
                self._reporters[test].addAssert(test, method_name, varList, e)
                raise
            self._reporters[test].addAssert(test, method_name, varList, None)

        setattr(Class, method_name, _assert_reporting_func)

    def set_reporter(self, test, reporter):
        self._reporters[test] = reporter

    def make_asserts_report(self, module_name, class_name, methods_pattern):
        Class = self._import(module_name, class_name)
        from re import match
        for method_name in dir(Class):
            if match(methods_pattern, method_name):
                self._make_assert_report(Class, method_name)

