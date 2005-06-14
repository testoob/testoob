def fix_include_path():
    from os.path import dirname, join, normpath
    module_path = normpath(join(dirname(__file__), "..", "src"))
    import sys
    sys.path.insert(0, module_path)

