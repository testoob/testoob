import parsing
parsing.parser.add_option("--html", metavar="FILE", help="output results in HTML")

def process_options(options):
    if options.html is not None:
        parsing.require_modules("--html", "Ft.Xml")
        from reporting import HTMLReporter
        parsing.kwargs["reporters"].append( HTMLReporter(filename=options.html) )

parsing.option_processors.append(process_options)
