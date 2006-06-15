import parsing
parsing.parser.add_option("--randomize-order", action="store_true", help="Randomize the test order")
parsing.parser.add_option("--randomize-seed", metavar="SEED", type="int", help="Seed for randomizing the test order, implies --randomize-order")

def non_negative_seed():
    """
    Returns a non-negative int as seed, based on time.time

    The seed is based on time.time, os.urandom may be used in the
    future (like it is in module 'random')
    """
    import time
    while True:
        result = hash(time.time()) # experiments show hash() works best
        if result >= 0:
            return result

def randomize_order(seed):
    if seed is None:
        seed = non_negative_seed()
    import sys
    print >>sys.stderr, "seed=%s" % seed
    import extracting
    parsing.kwargs["extraction_decorators"].append(extracting.randomize(seed))

def process_options(options):
    if options.randomize_order is not None or options.randomize_seed is not None:
        randomize_order(options.randomize_seed)

parsing.option_processors.append(process_options)
