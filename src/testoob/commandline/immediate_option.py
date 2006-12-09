import parsing
parsing.parser.add_option("-i", "--immediate", action="store_true", help="Immediate feedback about exceptions")

def process_options(options):
    import testoob.reporting
    testoob.reporting.options.immediate = options.immediate

parsing.option_processors.append(process_options)
