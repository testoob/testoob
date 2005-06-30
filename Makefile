PYTHON ?= python
DISTDIR = dist
APIDIR = $(DISTDIR)/api
WEBSITEDIR = $(DISTDIR)/website

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
	$(RM) MANIFEST

.PHONY: api
api:
	cd src; epydoc -o ../$(APIDIR) testoob

.phony: website
website:
	cd web; webgen; mv output ../$(WEBSITEDIR)

DISTUTILS_CMD = $(PYTHON) ./setup.py -q sdist --dist-dir=$(DISTDIR)
.PHONY: dist
dist: api
	$(RM) MANIFEST
	$(DISTUTILS_CMD) --formats=bztar
	$(DISTUTILS_CMD) --formats=gztar
