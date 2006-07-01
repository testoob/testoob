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

"Apply an XSL transformation to XMLReporter's xml output"

from xml import XMLReporter
import time
class XSLTReporter(XMLReporter):
    "This reporter uses an XSL transformation scheme to convert an XML output"

    class IXSLTApplier:
        "An interface for XSLT libs"
        def __init__(self, transform):
            "A constructor with the transformation to apply (string)"
            pass
        def apply(self, input, params={}):
            """Apply the transformation to the input and return the result.
            Params is a dictionary of extra parameters for the XSLT convertion"""
            pass

    class FourSuiteXSLTApplier(IXSLTApplier):
        "XSLT applier that uses 4Suite"
        def __init__(self, transform):
            from Ft.Xml.Xslt import Processor
            from Ft.Xml import InputSource
            self.processor = Processor.Processor()
            trans_source = InputSource.DefaultFactory.fromString(transform, "CONVERTER")
            self.processor.appendStylesheet(trans_source)

        def apply(self, input, params={}):
            from Ft.Xml import InputSource
            input_source = InputSource.DefaultFactory.fromString(input, "XML")
            return self.processor.run(input_source, topLevelParams=params)

    class WinCOMXSLTApplier(IXSLTApplier):
        "XSLT applier that uses window's COM interface to use a common windows XML library"
        def __init__(self,transform):
            import win32com.client
            self.trans_obj = win32com.client.Dispatch('Microsoft.XMLDOM')
            self.trans_obj.loadXML(transform)

        def apply(self, input, params= {}):
            import win32com.client
            input_obj = win32com.client.Dispatch('Microsoft.XMLDOM')
            input_obj.loadXML(input)
            return input_obj.transformNode(self.trans_obj)


    def __init__(self, filename, converter):
        XMLReporter.__init__(self)
        self.filename = filename
        self.converter = converter
    def done(self):
        XMLReporter.done(self)
        xslt_applier = self._create_xslt_applier()(self.converter)
        result = xslt_applier.apply(self.get_xml(), params = {u'date': unicode(time.asctime())})
        open(self.filename, "wt").write(result)

    def _create_xslt_applier(self):
        try:
            import Ft.Xml
            return XSLTReporter.FourSuiteXSLTApplier
        except:
            pass
        try:
            import win32com.client
            win32com.client.Dispatch('Microsoft.XMLDOM')
            return XSLTReporter.WinCOMXSLTApplier
        except:
            pass
        raise Exception,"Unable to find supported XSLT library (4Suite, MSXML)"

