import parsing
parsing.parser.add_option("--pdf", metavar="FILE", help="output results in PDF (requires ReportLab)")

def process_options(options):
    if options.pdf is not None:
        parsing.require_modules("--pdf", "reportlab")
        from testoob.reporting import PdfReporter
        parsing.kwargs["reporters"].append( PdfReporter(filename=options.pdf) )

parsing.option_processors.append(process_options)
