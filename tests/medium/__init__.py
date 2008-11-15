def suite():
    import testoob, testoob.capabilities
    if testoob.capabilities.c.f_back:
        return testoob.collecting.collect_from_files("test_*.py")
    else:
        # IronPython and others without f_back
        return testoob.collecting.collect_from_files("test_*.py", name=__name__, file=__file__)
