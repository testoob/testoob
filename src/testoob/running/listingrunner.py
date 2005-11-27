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

from baserunner import BaseRunner

class ListingRunner(BaseRunner):
    """Just list the test names, don't run them.
    """
    
    def __init__(self):
        self.history = _TestHistory()

    def run(self, fixture):
        self.history.record_fixture(fixture.get_fixture())

    def done(self):
        print self.history.get_string(max_functions_to_show=50)

class _TestHistory:
    def __init__(self):
        self.modules = {}

    def record_fixture(self, fixture):
        """Store the info about each fixture, to show them later.
        """
        from testoob.reporting import TestInfo
        fixture_info = TestInfo(fixture)
        self._class_function_list(fixture_info).append(fixture_info.funcinfo())

    def get_string(self, max_functions_to_show):
        """Show the test methods, if there are too many list the classes only.
        """
        result = []
        for (module_name, module_info) in self.modules.items():
            result.append("Module: %s (%s)" % \
                    (module_name, module_info["filename"]))
            for (class_name, functions) in module_info["classes"].items():
                result.append("\tClass: %s (%d test functions)" %\
                      (class_name, len(functions)))
                if self._num_functions() <= max_functions_to_show:
                    for func in functions:
                        result.append("\t\t%s()%s" % \
                                (func[0], func[1] and " - "+func[1] or ""))
        return "\n".join(result)

    def _module(self, fixture_info):
        self.modules.setdefault(
                fixture_info.module(),
                {
                    "filename": fixture_info.filename(),
                    "classes": {}
                })
        return self.modules[fixture_info.module()]

    def _class_function_list(self, fixture_info):
        classes_dict = self._module(fixture_info)["classes"]
        classes_dict.setdefault(fixture_info.classname(), [])
        return classes_dict[fixture_info.classname()]

    def _num_functions(self):
        result = 0
        for mod_info in self.modules.values():
            for functions in mod_info["classes"].values():
                result += len(functions)
        return result
