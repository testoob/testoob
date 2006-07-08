import parsing
parsing.parser.add_option("--repeat", metavar="NUM_TIMES", type="int", help="Repeat each test")

def process_options(options):
    if options.repeat is not None:
        from testoob.extracting import repeat
        parsing.kwargs["extraction_decorators"].append(repeat(options.repeat))

parsing.option_processors.append(process_options)
