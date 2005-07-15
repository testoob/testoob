"XSL converters for XML output"

def _read_file(filename):
    from os.path import join, dirname
    f = open(join(dirname(__file__), filename))
    try: return f.read()
    finally: f.close()

BASIC_CONVERTER = _read_file("html_report.xsl")
