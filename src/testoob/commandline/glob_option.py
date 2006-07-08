import parsing
parsing.parser.add_option("--glob", metavar="PATTERN", help="Filtering glob pattern")

def process_options(options):
    if options.glob is not None:
        from testoob.extracting import glob
        parsing.kwargs["extraction_decorators"].append(glob(options.glob))

parsing.option_processors.append(process_options)
