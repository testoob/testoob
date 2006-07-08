import parsing

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
    import sys
    if sys.platform == "win32":
        return True

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
        import sys
        if options.color_mode == "auto" and auto_color_support(sys.stderr):
            return True
        return False

    if color_output():
        from testoob.reporting import ColoredTextReporter
        parsing.kwargs["reporter_class"] = ColoredTextReporter

parsing.option_processors.append(process_options)
