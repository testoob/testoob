PYTHON ?= python
DISTDIR = dist
APIDIR = api
WEBSITEDIR = $(DISTDIR)/website
SUITEFILE = tests/alltests.py

.PHONY: all
all:
	@echo nothing to be done

.PHONY: test
test:
	$(PYTHON) $(SUITEFILE)

.PHONY: testall
testall:
	python2.4 $(SUITEFILE)
	python2.3 $(SUITEFILE)
	python2.2 $(SUITEFILE)

.PHONY: clean
clean:
	$(RM) `find . -name "*~"`
	$(RM) `find . -name "*.pyc"`
	$(RM) -r $(DISTDIR) $(APIDIR)
	$(RM) MANIFEST

.PHONY: api
api:
	cd src; epydoc -o ../$(APIDIR) testoob

.phony: website
website:
	cd web; webgen; mv output ../$(WEBSITEDIR)

DISTUTILS_CMD = $(PYTHON) ./setup.py -q sdist --dist-dir=$(DISTDIR)
.PHONY: dist
dist:
	$(RM) MANIFEST
	$(DISTUTILS_CMD) --formats=bztar
	$(DISTUTILS_CMD) --formats=gztar
