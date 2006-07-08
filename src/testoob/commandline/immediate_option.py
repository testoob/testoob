import parsing
parsing.parser.add_option("-i", "--immediate", action="store_true", help="Immediate feedback about exceptions")

def process_options(options):
    parsing.kwargs["immediate"] = options.immediate

parsing.option_processors.append(process_options)
