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

"Common functionality for reporting"

# Code mostly taken from PyUnit (unittest.py)

# Constructing meaningful report strings from exception info
def exc_info_to_string(err, test):
    "Converts a sys.exc_info()-style tuple of values into a string."
    import traceback
    exctype, value, tb = err
    # Skip test runner traceback levels
    while tb and is_framework_traceback(tb):
        tb = tb.tb_next
    if exctype is test.failure_exception_type():
        # Skip assert*() traceback levels
        length = count_framework_traceback_levels(tb)
        return ''.join(traceback.format_exception(exctype, value, tb, length))
    return ''.join(traceback.format_exception(exctype, value, tb))

def is_framework_traceback(tb):
    globals = tb.tb_frame.f_globals
    return globals.has_key('__unittest') or globals.has_key('__testoob')

def count_framework_traceback_levels(tb):
    length = 0
    while tb and not is_framework_traceback(tb):
        length += 1
        tb = tb.tb_next
    return length
