import parsing
parsing.parser.add_option("-l", "--list", action="store_true", help="List the test classes and methods found")
parsing.parser.add_option("--list-formatted", metavar="FORMATTER", help="Like option '-l', just formatted (e.g. csv).")

def process_options(options):
    if options.list_formatted:
        from running import ListingRunner
        parsing.kwargs["runner"] = ListingRunner(output_format=options.list_formatted)
    elif options.list is not None:
        from running import ListingRunner
        parsing.kwargs["runner"] = ListingRunner()

parsing.option_processors.append(process_options)
