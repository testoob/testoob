import parsing
parsing.parser.add_option("--time-each-test", action="store_true", help="Report the total time for each test")

def process_options(options):
    import testoob.reporting.options
    testoob.reporting.options.time_each_test = options.time_each_test

parsing.option_processors.append(process_options)
