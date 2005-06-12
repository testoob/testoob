PYTHON ?= python
DISTDIR = dist
APIDIR = api

.PHONY: all
all:
	@echo nothing to be done

.PHONY: test
test:
	$(PYTHON) ./tests/alltests.py

.PHONY: clean
clean:
	$(RM) `find . -name "*~"`
	$(RM) `find . -name "*.pyc"`
	$(RM) -r $(DISTDIR)
	$(RM) -r $(APIDIR)
	$(RM) MANIFEST

.PHONY: api
api:
	cd src; epydoc -o ../$(APIDIR) testoob

DISTUTILS_SDIST_OPTIONS = --formats=bztar --dist-dir=$(DISTDIR)
.PHONY: dist
dist: api
	$(RM) MANIFEST
	$(PYTHON) ./setup.py -q sdist $(DISTUTILS_SDIST_OPTIONS)
