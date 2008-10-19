import parsing, sys

color_choices = ["never", "always", "auto"]
parsing.parser.add_option(
    "--color-mode",
    metavar = "WHEN",
    type    = "choice",
    choices = color_choices,
    default = "auto",
    help    = "When should output be in color? Choices are " + str(color_choices) + ", default is '%default'"
)

def auto_color_support(stream):
    if sys.platform.startswith("win"):
        try:
            import ctypes
            return _win_ctypes_color_support()
        except ImportError:
            pass

        # 'True' by default
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

def process_options(options):
    def color_output():
        if options.color_mode == "always":
            return True
        # TODO: currently hard-coded to sys.stderr, fix this
        if options.color_mode == "auto" and auto_color_support(sys.stderr):
            return True
        return False

    if color_output():
        from testoob.reporting import ColoredTextReporter
        parsing.kwargs["reporter_class"] = ColoredTextReporter

parsing.option_processors.append(process_options)
