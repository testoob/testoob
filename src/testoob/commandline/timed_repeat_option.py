import parsing
parsing.parser.add_option("--timed-repeat", metavar="SECONDS", type="float", help="Repeat each test, for a limited time")

def process_options(options):
    if options.timed_repeat is not None:
        from testoob.running import fixture_decorators
        parsing.kwargs["fixture_decorators"].append(
                fixture_decorators.get_timed_fixture(options.timed_repeat))

parsing.option_processors.append(process_options)
