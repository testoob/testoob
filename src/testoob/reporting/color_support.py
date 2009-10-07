# Testoob, Python Testing Out Of (The) Box
# Copyright (C) 2005-2009 The Testoob Team
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

import sys, os

DISABLE_COLOR_SUPPORT_ENV_VAR_NAME = "TESTOOB_DISABLE_COLOR_SUPPORT"
def can_autodetect_color_support():
    # On Windows, we can only autodetect if ctypes is available
    if sys.platform.startswith("win"):
        try:
            import ctypes
            return True
        except ImportError:
            return False

    # On POSIX, autodetection is strong enough to consider it always working
    return True

def auto_color_support(stream):
    if sys.platform.startswith("win"):
        try:
            import ctypes
            return _win_ctypes_color_support()
        except ImportError:
            pass

        # TODO: use win32console if available, and add support to setcolor.exe
        # as a final fallback

        # Check if explicitly disabled via environment
        if DISABLE_COLOR_SUPPORT_ENV_VAR_NAME in os.environ:
            return False

        # 'True' by default on Windows, because we can currently only
        # autodetect if ctypes is available
        return True

    return _curses_color_support(stream)

def _win_ctypes_color_support():
    import ctypes
    STD_OUTPUT_HANDLE = -11
    out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    csbi = ctypes.create_string_buffer(22)
    res = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(out_handle, csbi)
    return res != 0

def _curses_color_support(stream):
    if not hasattr(stream, "isatty"):
        return False
    if not stream.isatty():
        return False # auto color only on TTYs

    try:
        import curses
        curses.setupterm()
        return curses.tigetnum("colors") > 2
    except:
        # guess false in case of error
        return False

