import parsing
parsing.parser.add_option("-s", "--silent", action="store_true", help="no output to terminal")

def process_options(options):
    parsing.kwargs["silent"] = options.silent

parsing.option_processors.append(process_options)
