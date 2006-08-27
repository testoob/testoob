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

"Color text stream reporting"

import os, sys
try:
    import subprocess
except ImportError:
    from testoob.compatibility import subprocess

ANSI_CODES = {
    "reset"     : "\x1b[0m",
    "bold"      : "\x1b[01m",
    "teal"      : "\x1b[36;06m",
    "turquoise" : "\x1b[36;01m",
    "fuscia"    : "\x1b[35;01m",
    "purple"    : "\x1b[35;06m",
    "blue"      : "\x1b[34;01m",
    "darkblue"  : "\x1b[34;06m",
    "green"     : "\x1b[32;01m",
    "darkgreen" : "\x1b[32;06m",
    "yellow"    : "\x1b[33;01m",
    "brown"     : "\x1b[33;06m",
    "red"       : "\x1b[31;01m",
}

from textstream import TextStreamReporter, StreamWriter
class TerminalColorWriter(StreamWriter):
    def __init__(self, stream, color):
        StreamWriter.__init__(self, stream)
        self.code  = ANSI_CODES[color]
        self.reset = ANSI_CODES["reset"]
    def write(self, s):
        StreamWriter.write(self, self.code)
        StreamWriter.write(self, s)
        StreamWriter.write(self, self.reset)

WIN32_SETCOLOR_CODES = {
    "reset"  : "d",
    "red"    : "r",
    "green"  : "g",
    "yellow" : "y",
}

class Win32ColorWriterWithExecutable(StreamWriter):
    setcolor_path = os.path.join(sys.prefix, "testoob", "setcolor.exe")
    setcolor_available = os.path.isfile(setcolor_path)

    def __init__(self, stream, color):
        StreamWriter.__init__(self, stream)
        self.code  = WIN32_SETCOLOR_CODES[color]
        self.reset = WIN32_SETCOLOR_CODES["reset"]

    def _call_setcolor(self, code):
        if self.setcolor_available:
            subprocess.Popen(r'"%s" %s' % (self.setcolor_path, code)).wait()

    def write(self, s):
        self._call_setcolor(self.code)
        StreamWriter.write(self, s)
        self._call_setcolor(self.reset)

class Win32ConsoleColorWriter(StreamWriter):
    def _out_handle(self):
        import win32console
        return win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)
    out_handle = property(_out_handle)

    def _codes(self):
        from win32console import FOREGROUND_RED, FOREGROUND_GREEN, FOREGROUND_INTENSITY
        return {
            "reset"  : self.out_handle.GetConsoleScreenBufferInfo()['Attributes'],
            "red"    : FOREGROUND_RED | FOREGROUND_INTENSITY,
            "green"  : FOREGROUND_GREEN | FOREGROUND_INTENSITY,
            "yellow" : FOREGROUND_GREEN | FOREGROUND_RED | FOREGROUND_INTENSITY,
        }
    CODES = property(_codes)

    def __init__(self, stream, color):
        StreamWriter.__init__(self, stream)
        self.code  = self.CODES[color]
        self.reset = self.CODES["reset"]

    def write(self, s):
        self.out_handle.SetConsoleTextAttribute( self.code )
        StreamWriter.write(self, s)
        self.out_handle.SetConsoleTextAttribute( self.reset )

def color_writers_creator(writer_class):
    class ColorWriters:
        def __init__(self, stream):
            self.normal  = StreamWriter(stream)
            self.success = writer_class(stream, "green")
            self.failure = writer_class(stream, "red")
            self.warning = writer_class(stream, "yellow")
    return ColorWriters

def create_colored_reporter(writer_class):
    class ColoredReporter(TextStreamReporter):
        def __init__(self, *args, **kwargs):
            kwargs["create_writers"] = color_writers_creator(writer_class)
            TextStreamReporter.__init__(self, *args, **kwargs)
    return ColoredReporter

def choose_color_writer():
    if sys.platform != "win32":
        return TerminalColorWriter

    try:
        import win32console
        return Win32ConsoleColorWriter
    except ImportError:
        pass

    return Win32ColorWriterWithExecutable

ColoredTextReporter = create_colored_reporter( choose_color_writer() )
