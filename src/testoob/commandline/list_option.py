import parsing
parsing.parser.add_option("-l", "--list", action="store_true", help="List the test classes and methods found")
parsing.parser.add_option("--list-formatted", metavar="FORMATTER", help="Like option '-l', just formatted (e.g. csv).")

def process_options(options):
    from testoob.running import ListingRunner
    if options.list_formatted:
        parsing.kwargs["runner"] = ListingRunner(output_format=options.list_formatted)
    elif options.list is not None:
        parsing.kwargs["runner"] = ListingRunner()

parsing.option_processors.append(process_options)
