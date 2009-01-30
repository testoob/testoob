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
    def get_bgcolor(self):
        return "unknown"


class WindowsColorBaseWriter(StreamWriter):
    """
    All Windows writers set the color without writing special control
    characters, so this class is convenient.
    """
    FOREGROUND_BLUE      = 0x0001 # text color contains blue.
    FOREGROUND_GREEN     = 0x0002 # text color contains green.
    FOREGROUND_RED       = 0x0004 # text color contains red.
    FOREGROUND_INTENSITY = 0x0008 # text color is intensified.
    BACKGROUND_BLUE      = 0x0010 # background color contains blue.
    BACKGROUND_GREEN     = 0x0020 # background color contains green.
    BACKGROUND_RED       = 0x0040 # background color contains red.
    BACKGROUND_INTENSITY = 0x0080 # background color is intensified.

    def __init__(self, stream, color):
        StreamWriter.__init__(self, stream)
        self.reset = self._get_color()
        self.background = self.reset & 0xf0
        CODES = {
            "red"    : self.FOREGROUND_RED | self.FOREGROUND_INTENSITY | self.background,
            "green"  : self.FOREGROUND_GREEN | self.FOREGROUND_INTENSITY | self.background,
            "yellow" : self.FOREGROUND_GREEN | self.FOREGROUND_RED | self.FOREGROUND_INTENSITY | self.background,
            "blue"   : self.FOREGROUND_BLUE | self.FOREGROUND_INTENSITY | self.background
        }
        self.code  = CODES[color]

    def write(self, s):
        self._set_color(self.code)
        StreamWriter.write(self, s)
        self._set_color(self.reset)

    def get_bgcolor(self):
        WHITE = self.BACKGROUND_RED | self.BACKGROUND_GREEN | self.BACKGROUND_BLUE | self.BACKGROUND_INTENSITY
        YELLOW = self.BACKGROUND_RED | self.BACKGROUND_GREEN | self.BACKGROUND_INTENSITY
        if self.background in [WHITE, YELLOW]:
            return "light"
        else:
            return "dark"  


class Win32ColorWriterWithExecutable(WindowsColorBaseWriter):
    setcolor_path = os.path.join(sys.prefix, "testoob", "setcolor.exe")
    setcolor_available = os.path.isfile(setcolor_path)
    if not setcolor_available:
        setcolor_path = os.path.join('other','setcolor.exe')
        setcolor_available = os.path.isfile(setcolor_path)

    def _set_color(self, code):
        # TODO: fail in advance if setcolor.exe isn't available?
        if self.setcolor_available:
            try:
                import subprocess
            except ImportError:
                from testoob.compatibility import subprocess
            subprocess.Popen('"%s" set %d' % (self.setcolor_path, code)).wait()

    def _get_color(self):
        if self.setcolor_available:
            try:
                import subprocess
            except ImportError:
                from testoob.compatibility import subprocess
            get_pipe = subprocess.Popen('"%s" get' % (self.setcolor_path),
                        stdout=subprocess.PIPE)
            color_code, _ = get_pipe.communicate()
            return int(color_code)
        else:
            return 0x0f


class Win32ConsoleColorWriter(WindowsColorBaseWriter):
    def _out_handle(self):
        import win32console
        return win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)
    out_handle = property(_out_handle)
        
    def _set_color(self, code):
        self.out_handle.SetConsoleTextAttribute( code )

    def _get_color(self):
        return self.out_handle.GetConsoleScreenBufferInfo()['Attributes']
          

class WindowsCtypesColorWriter(WindowsColorBaseWriter):
    # Constants from the Windows API
    STD_OUTPUT_HANDLE = -11
    
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

    def _set_color(self, code):
        import ctypes
        ctypes.windll.kernel32.SetConsoleTextAttribute(self.out_handle, code)

    def _get_color(self):
        return self.console_screen_buffer_info["wattr"]


def color_writers_creator(writer_class):
    class ColorWriters:
        def _get_warning_color(self, bgcolor):
            import options
            if options.bgcolor != "auto":
                bgcolor = options.bgcolor
            bg_mapping = {"dark": "yellow", "light": "blue", "unknown": "yellow" }
            warning_color = bg_mapping[bgcolor]
            return warning_color
            
        def __init__(self, stream):
            self.normal  = StreamWriter(stream)
            self.success = writer_class(stream, "green")
            self.failure = writer_class(stream, "red")
            bgcolor = self.success.get_bgcolor()
            self.warning = writer_class(stream, self._get_warning_color(bgcolor))
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
        #print "DEBUG: using", os.environ["TESTOOB_COLOR_WRITER"]
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
