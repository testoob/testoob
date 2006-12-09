import parsing
parsing.parser.add_option("-s", "--silent", action="store_true", help="no output to terminal")

def process_options(options):
    import testoob.reporting
    testoob.reporting.options.silent = options.silent

parsing.option_processors.append(process_options)
