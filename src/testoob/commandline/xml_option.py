import parsing
parsing.parser.add_option("--xml", metavar="FILE", help="output results in XML")

def process_options(options):
    if options.xml is not None:
        from testoob.reporting import XMLFileReporter
        parsing.kwargs["reporters"].append( XMLFileReporter(filename=options.xml) )

parsing.option_processors.append(process_options)
