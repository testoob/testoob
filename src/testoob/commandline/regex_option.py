import parsing
parsing.parser.add_option("--regex", help="Filtering regular expression")

def process_options(options):
    if options.regex is not None:
        import extracting
        parsing.kwargs["extraction_decorators"].append(extracting.regex(options.regex))

parsing.option_processors.append(process_options)
