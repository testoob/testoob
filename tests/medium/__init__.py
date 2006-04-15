def suite():
    import testoob
    return testoob.collecting.collect_from_files("test_*.py")
