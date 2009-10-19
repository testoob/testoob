import parsing
bgcolor_choices = ["auto", "light", "dark"]
parsing.parser.add_option(
    "--bgcolor",
    metavar = "WHEN",
    type    = "choice",
    choices = bgcolor_choices,
    default = "auto",
    help    = """What's the background color of the terminal. This is used to determine a readable warning color. Choices are """ + str(bgcolor_choices) + """, default is '%default'"""
)

def process_options(options):
    import testoob.reporting
    testoob.reporting.options.bgcolor = options.bgcolor

parsing.option_processors.append(process_options)
