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

"getting information about tests"

def create_test_info(arg):
    """
    Factory method for creating TestInfo instances.
    """
    if isinstance(arg, TestInfo):
        return arg

    return TestInfo(arg)

class TestInfo:
    """
    An interface for getting information about tests.
    Reporters receive instances of this class.
    """
    def __init__(self, fixture):
        self.fixture = fixture
    
    def module(self):
        return self.fixture.__module__

    def filename(self):
        import sys
        try:
            return sys.modules[self.module()].__file__
        except KeyError:
            return "unknown file"

    def classname(self):
        return self.fixture.__class__.__name__

    def funcname(self):
        # parsing id() because the function name is a private fixture field
        return self.fixture.id().split(".")[-1]

    def extrainfo(self):
        return self.fixture._testoob_extra_description

    def extrafuncname(self):
        return "%s%s" % (self.funcname(), self.extrainfo())

    def docstring(self):
        if getattr(self.fixture, self.funcname()).__doc__:
            return getattr(self.fixture, self.funcname()).__doc__.splitlines()[0]
        return ""

    def funcinfo(self):
        return (self.funcname(), self.docstring(), self.extrainfo())

    def failure_exception_type(self): # TODO: do we need this?
        return self.fixture.failureException

    def id(self): # TODO: do we need this?
        return self.fixture.id()

    def short_description(self): # TODO: do we need this?
        return self.fixture.shortDescription()

    def __str__(self):
        return str(self.fixture)

    # should be usable as dictionary keys, so define __hash__ and __cmp__
    def __unique_string_repr(self):
        return "%s - %s" % (hash(self), str(self))

    def __cmp__(self, other):
        try:
            return cmp(self.fixture, other.fixture)
        except AttributeError:
            return cmp(self.__unique_string_repr(), other.__unique_string_repr())

    def __hash__(self):
        return hash(self.fixture)

from testoob.utils import add_fields_pickling
add_fields_pickling(TestInfo)
