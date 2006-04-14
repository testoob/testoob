# Testoob, Python Testing Out Of (The) Box
# Copyright (C) 2005 The Testoob Team
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

"Report results in HTML, using an XSL transformation"

# TODO: insert the converter here
from xslt import XSLTReporter
class HTMLReporter(XSLTReporter):
    def __init__(self, filename):
        import xslconverters
        XSLTReporter.__init__(self, filename, xslconverters.BASIC_CONVERTER)

