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

"Color text stream reporting"

from textstream import TextStreamReporter
class ColoredTextReporter(TextStreamReporter):
    "Uses ANSI escape sequences to color the output of a text reporter"
    codes = {"reset":"\x1b[0m",
             "bold":"\x1b[01m",
             "teal":"\x1b[36;06m",
             "turquoise":"\x1b[36;01m",
             "fuscia":"\x1b[35;01m",
             "purple":"\x1b[35;06m",
             "blue":"\x1b[34;01m",
             "darkblue":"\x1b[34;06m",
             "green":"\x1b[32;01m",
             "darkgreen":"\x1b[32;06m",
             "yellow":"\x1b[33;01m",
             "brown":"\x1b[33;06m",
             "red":"\x1b[31;01m",
             "darkred":"\x1b[31;06m"}

    def __init__(self, stream, descriptions, verbosity, immediate):
        TextStreamReporter.__init__(self, stream, descriptions, verbosity, immediate)

    def _red(self, str):
        "Make it red!"
        return ColoredTextReporter.codes['red'] + str + ColoredTextReporter.codes['reset']

    def _green(self, str):
        "make it green!"
        return ColoredTextReporter.codes['green'] + str + ColoredTextReporter.codes['reset']
    
    def _yellow(self, str):
        "make it yellow!"
        return ColoredTextReporter.codes['yellow'] + str + ColoredTextReporter.codes['reset']

    def _decorateFailure(self, errString):
        return self._red(errString)

    def _decorateSuccess(self, sccString):
        return self._green(sccString)

    def _decorateWarning(self, warString):
        return self._yellow(warString)

