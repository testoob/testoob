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

def _import(package_name, class_name):
    return getattr(__import__(package_name), class_name)

def _create_message(method_name, variables_names, variables_values):
    msg = "(" + method_name + ") "
    msg += " ".join([name + ": \"" + str(value) + "\"" for name, value in zip(variables_names, variables_values)])
    return msg

def _make_method_verbose(Class, method_name, reporter):
    variables = eval("Class.%s" % method_name).func_code.co_varnames
    setattr(Class, "_real_function_%s" % method_name, eval("Class.%s" % method_name))
    method = eval("Class._real_function_%s" % method_name)
    def _new_func(*args):
        msg = _create_message(method_name, variables[1:], args[1:])
        try:
            method(*args)
        except:
            reporter.addVassert(msg, '-')
            raise
        reporter.addVassert(msg, '+')

    setattr(Class, method_name, _new_func)

def make_methods_verbose(module_name, class_name, methods_pattern, reporter):
    Class = _import(module_name, class_name)
    from re import match
    for method_name in dir(Class):
        if match(methods_pattern, method_name):
            _make_method_verbose(Class, method_name, reporter)

