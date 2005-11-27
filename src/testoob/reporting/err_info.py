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

# TODO: fix the 'exc_info is None means no error' idiom
#       Some options:
#       - choose different semantics
#       - make the methods returning parts of exc_info return None if exc_info
#         is None
class ErrInfo:
    """
    An interface for getting information about test errors.
    Reporters receive instances of this class.
    """
    def __init__(self, test, exc_info):
        "if exc_info is None, it means there was no error"
        self.test = test
        self.exc_info = exc_info

    def __str__(self):
        try:
            from common import _exc_info_to_string
            from testinfo import TestInfo
            return _exc_info_to_string(self.exc_info, TestInfo(self.test))
        except:
            return "Error converting to string"

    def exception_type(self):
        return str(self.exc_info[0])

    def exception_value(self):
        return str(self.exc_info[1])

    def traceback(self):
        return self.exc_info[2]

    def no_error(self):
        return self.exc_info == None
    
from testoob.utils import add_fields_pickling
add_fields_pickling(ErrInfo)
