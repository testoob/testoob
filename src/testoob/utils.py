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

def add_fields_pickling(klass):
    """
    Add pickling for 'fields' classes.

    A 'fields' class is a class who's methods all act as fields - accept no
    arguments and for a given class's state always return the same value.

    Useful for 'fields' classes that contain unpickleable members.
    Used in TestOOB, http://testoob.sourceforge.net

    A contrived example for a 'fields' class:

      class Titles:
        def __init__(self, name):
          self.name = name
        def dr(self):
          return "Dr. " + self.name
        def mr(self):
          return "Mr. " + self.name

    See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/456363
    """
    def state_extractor(self):
        from types import MethodType

        result = {}

        for attr_name in dir(self):
            if attr_name == "__init__":
                continue # skip constructor

            attr = getattr(self, attr_name)
            if type(attr) == MethodType:
                try:
                    result[attr_name] = attr() # call the method
                except TypeError:
                    raise TypeError("""not a "fields" class, problem with method '%s'""" % attr_name)

        return result

    def build_from_state(self, state):
        for name in state.keys():
            # set the default name argument to prevent overwriting the name
            setattr(self, name, lambda name=name:state[name])

    klass.__getstate__ = state_extractor
    klass.__setstate__ = build_from_state

