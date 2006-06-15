import parsing
parsing.parser.add_option("--pbar", action="store_true", help="Show a progress bar")

def process_options(options):
    if options.pbar is not None:
        from reporting.progress_bar import ProgressBarReporter
        parsing.kwargs["reporters"].append( ProgressBarReporter() )

parsing.option_processors.append(process_options)
