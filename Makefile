PYTHON ?= python
DISTDIR = $(CURDIR)/dist
BUILDDIR = $(CURDIR)/build
APIDIR = $(BUILDDIR)/api
WEBSITEDIR = $(DISTDIR)/website
SUITEFILE = tests/alltests.py
SOURCES = $(wildcard src/testoob/*.py)
WEBSITE_SOURCES = web/src/*.page web/src/*.template web/src/*.info
VERSION = __TESTOOB_VERSION__
WEBDISTFILE = $(DISTDIR)/testoob_website-$(VERSION).tar.bz2

.PHONY: all
all:
	@echo nothing to be done

test_with = PYTHONPATH=src:$(PYTHONPATH) TESTOOB_DEVEL_TEST=1 $(1) ./src/testoob/testoob $(SUITEFILE) suite $(ARGS) $(2)
.PHONY: test
test:
	$(call test_with,$(PYTHON))

.PHONY: testall
testall:
	$(call test_with,python2.6)
	$(call test_with,python2.5)
	$(call test_with,python2.4)
	$(call test_with,python2.3)
	$(call test_with,python2.2)

.PHONY: smoke
smoke:
	$(call test_with,python,--regex=testFailureRunQuiet)

ISOLATED_TEST_CMD = ./scripts/isolated_test.py --test-args="$(ARGS)"

.PHONY: isolated_test
isolated_test:
	$(ISOLATED_TEST_CMD)

.PHONY: isolated_testall
isolated_testall:
	$(ISOLATED_TEST_CMD) --python=python2.4
	$(ISOLATED_TEST_CMD) --python=python2.5
	$(ISOLATED_TEST_CMD) --python=python2.3
	$(ISOLATED_TEST_CMD) --python=python2.2 --install-python=python

.PHONY: commit_stats
commit_stats:
	svn log `svn info|grep '^Repository Root'|awk '{print $$3}'` | grep '^r[0-9].*lines\?'|cut -d'|' -f2|sort|uniq -c|sort -n

.PHONY: clean
clean:
	zsh --nullglob -c 'rm -f **/{*{~,.pyc},svn-commit*.tmp*}'
	$(RM) -r $(DISTDIR) $(BUILDDIR) web/output
	$(RM) MANIFEST

$(APIDIR): $(SOURCES)
	mkdir -p $(APIDIR)
	epydoc -o $(APIDIR) --url http://testoob.sourceforge.net -n Testoob -q $(SOURCES)

$(WEBSITEDIR): $(DISTDIR) $(APIDIR) $(WEBSITE_SOURCES)
	cd web && webgen && rm -fr $(WEBSITEDIR) && cp -R output $(WEBSITEDIR) && cp -R $(APIDIR) $(WEBSITEDIR) && chmod -R og+rX $(WEBSITEDIR)

.phony: web
web: $(WEBSITEDIR)

$(DISTDIR):
	mkdir $(DISTDIR)

distutils = $(PYTHON) ./setup.py -q $(1) --dist-dir=$(DISTDIR) $(2)
distutils_sdist = $(call distutils,sdist,--format=$(strip $(1)))
distutils_wininst = $(call distutils,bdist_wininst)

.PHONY: distfiles
distfiles: $(DISTDIR)
	$(RM) MANIFEST
	$(call distutils_sdist, gztar)
	$(call distutils_sdist, bztar)
	$(call distutils_wininst)

.PHONY: dist
dist: $(WEBSITEDIR) distfiles
	cd $(WEBSITEDIR); tar jcf $(WEBDISTFILE) .
