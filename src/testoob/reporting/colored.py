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

from textstream import StreamWriter
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

class WindowsColorBaseWriter(StreamWriter):
    """
    All Windows writers set the color without writing special control
    characters, so this class is convenient.
    """
    def write(self, s):
        self._set_color(self.code)
        StreamWriter.write(self, s)
        self._set_color(self.reset)

class Win32ColorWriterWithExecutable(WindowsColorBaseWriter):
    setcolor_path = os.path.join(sys.prefix, "testoob", "setcolor.exe")
    setcolor_available = os.path.isfile(setcolor_path)

    def __init__(self, stream, color):
        StreamWriter.__init__(self, stream)
        self.code  = WIN32_SETCOLOR_CODES[color]
        self.reset = WIN32_SETCOLOR_CODES["reset"]

    def _set_color(self, code):
        # TODO: fail in advance if setcolor.exe isn't availble?
        if self.setcolor_available:
            try:
                import subprocess
            except ImportError:
                from testoob.compatibility import subprocess
            subprocess.Popen(r'"%s" %s' % (self.setcolor_path, code)).wait()

class Win32ConsoleColorWriter(WindowsColorBaseWriter):
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

    def _set_color(self, code):
        self.out_handle.SetConsoleTextAttribute( code )

class WindowsCtypesColorWriter(WindowsColorBaseWriter):
    # Constants from the Windows API
    STD_OUTPUT_HANDLE = -11

    FOREGROUND_BLUE      = 0x0001 # text color contains blue.
    FOREGROUND_GREEN     = 0x0002 # text color contains green.
    FOREGROUND_RED       = 0x0004 # text color contains red.
    FOREGROUND_INTENSITY = 0x0008 # text color is intensified.
    
    def _out_handle(self):
        import ctypes
        return ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
    out_handle = property(_out_handle)

    def _console_screen_buffer_info(self):
        # Based on IPython's winconsole.py, written by Alexander Belchenko
        import ctypes, struct
        csbi = ctypes.create_string_buffer(22)
        res = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(self.out_handle, csbi)
        assert res

        (bufx, bufy, curx, cury, wattr,
         left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)

        return {
            "bufx" : bufx,
            "bufy" : bufy,
            "curx" : curx,
            "cury" : cury,
            "wattr" : wattr,
            "left" : left,
            "top" : top,
            "right" : right,
            "bottom" : bottom,
            "maxx" : maxx,
            "maxy" : maxy,
        }
    console_screen_buffer_info = property(_console_screen_buffer_info)

    def _codes(self):
        return {
            "reset"  : self.console_screen_buffer_info["wattr"],
            "red"    : self.FOREGROUND_RED | self.FOREGROUND_INTENSITY,
            "green"  : self.FOREGROUND_GREEN | self.FOREGROUND_INTENSITY,
            "yellow" : self.FOREGROUND_GREEN | self.FOREGROUND_RED | self.FOREGROUND_INTENSITY,
        }
    CODES = property(_codes)

    def __init__(self, stream, color):
        StreamWriter.__init__(self, stream)
        self.code = self.CODES[color]
        self.reset = self.CODES["reset"]

    def _set_color(self, code):
        import ctypes
        ctypes.windll.kernel32.SetConsoleTextAttribute(self.out_handle, code)

def color_writers_creator(writer_class):
    class ColorWriters:
        def __init__(self, stream):
            self.normal  = StreamWriter(stream)
            self.success = writer_class(stream, "green")
            self.failure = writer_class(stream, "red")
            self.warning = writer_class(stream, "yellow")
    return ColorWriters

from textstream import TextStreamReporter
def create_colored_reporter(writer_class):
    class ColoredReporter(TextStreamReporter):
        def __init__(self, *args, **kwargs):
            kwargs["create_writers"] = color_writers_creator(writer_class)
            TextStreamReporter.__init__(self, *args, **kwargs)
    return ColoredReporter

def choose_color_writer():
    if "TESTOOB_COLOR_WRITER" in os.environ:
        print "DEBUG: using", os.environ["TESTOOB_COLOR_WRITER"]
        return eval(os.environ["TESTOOB_COLOR_WRITER"])

    if sys.platform != "win32":
        return TerminalColorWriter

    try:
        import win32console
        return Win32ConsoleColorWriter
    except ImportError:
        pass

    try:
        import ctypes
        return WindowsCtypesColorWriter
    except ImportError:
        pass

    return Win32ColorWriterWithExecutable

ColoredTextReporter = create_colored_reporter( choose_color_writer() )
