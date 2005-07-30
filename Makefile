PYTHON ?= python
DISTDIR = $(CURDIR)/dist
BUILDDIR = $(CURDIR)/build
APIDIR = $(BUILDDIR)/api
WEBSITEDIR = $(HOME)/public_html/testoob
SUITEFILE = tests/alltests.py
SOURCES = $(wildcard src/testoob/*.py)
WEBSITE_SOURCES = web/src/*.page web/src/*.template web/src/*.info

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
	$(RM) -r $(DISTDIR) $(BUILDDIR) web/output
	$(RM) MANIFEST

$(APIDIR): $(SOURCES)
	mkdir -p $(APIDIR)
	epydoc -o $(APIDIR) --url http://testoob.sourceforge.net -n TestOOB -q $(SOURCES)

$(WEBSITEDIR): $(APIDIR) $(WEBSITE_SOURCES)
	cd web && webgen && rm -fr $(WEBSITEDIR) && cp -R output $(WEBSITEDIR) && cp -R $(APIDIR) $(WEBSITEDIR) && chmod -R og+rX $(WEBSITEDIR)

.phony: web
web: $(WEBSITEDIR)

DISTUTILS_CMD = $(PYTHON) ./setup.py -q sdist --dist-dir=$(DISTDIR)
.PHONY: dist
dist:
	$(RM) MANIFEST
	$(DISTUTILS_CMD) --formats=bztar
	$(DISTUTILS_CMD) --formats=gztar
