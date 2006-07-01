import parsing
parsing.parser.add_option("--processes", metavar="NUM_PROCESSES", type="int", help="Run in multiple processes, use Pyro if available")
parsing.parser.add_option("--processes_pyro", metavar="NUM_PROCESSES", type="int", help="Run in multiple processes, requires Pyro")
parsing.parser.add_option("--processes_old", metavar="NUM_PROCESSES", type="int", help="Run in multiple processes, old implementation")

def enable_processes_pyro(nprocesses):
    parsing.require_posix("--processes_pyro")
    parsing.require_modules("--processes_pyro", "Pyro")
    from testoob.running import PyroRunner
    parsing.kwargs["runner"] = PyroRunner(max_processes = nprocesses)

def enable_processes_old(nprocesses):
    parsing.require_posix("--processes_old")
    from testoob.running import ProcessedRunner
    parsing.kwargs["runner"] = ProcessedRunner(max_processes = nprocesses)

def process_options(options):
    if options.processes_pyro is not None:
        enable_processes_pyro(options.processes_pyro)
        
    if options.processes_old is not None:
        enable_processes_old(options.processes_old)

    if options.processes is not None:
        try:
            enable_processes_pyro(options.processes)
        except ArgumentsError:
            enable_processes_old(options.processes)

parsing.option_processors.append(process_options)
