import parsing
parsing.parser.add_option("--junit-xml", metavar="FILE", help="output results in JUnit XML (Ant-style with Hudson flavors)")

def process_options(options):
    if options.junit_xml is not None:
        from testoob.reporting import JUnitXMLFileReporter
        parsing.kwargs["reporters"].append( JUnitXMLFileReporter(filename=options.junit_xml) )

parsing.option_processors.append(process_options)
