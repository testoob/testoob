PYTHON ?= python
DISTDIR = $(CURDIR)/dist
BUILDDIR = $(CURDIR)/build
APIDIR = $(BUILDDIR)/api
WEBSITEDIR = $(HOME)/public_html/testoob
SUITEFILE = tests/alltests.py
SOURCES = $(wildcard src/testoob/*.py)
WEBSITE_SOURCES = web/src/*.page web/src/*.template web/src/*.info
VERSION = __TESTOOB_VERSION__
WEBDISTFILE = $(DISTDIR)/testoob_website-$(VERSION).tar.bz2

.PHONY: all
all:
	@echo nothing to be done

test_with = TESTOOB_DEVEL_TEST=1 $(1) ./src/testoob/testoob $(SUITEFILE) suite $(ARGS)
.PHONY: test
test:
	$(call test_with,python)

.PHONY: testall
testall:
	$(call test_with,python2.4)
	$(call test_with,python2.3)
	$(call test_with,python2.2)

.PHONY: isolated_test
isolated_test:
	./scripts/isolated_test.py

.PHONY: isolated_testall
isolated_testall:
	./scripts/isolated_test.py --python=python2.4
	./scripts/isolated_test.py --python=python2.3
	./scripts/isolated_test.py --python=python2.2 --install-python=python

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

$(WEBSITEDIR): $(APIDIR) $(WEBSITE_SOURCES)
	cd web && webgen && rm -fr $(WEBSITEDIR) && cp -R output $(WEBSITEDIR) && cp -R $(APIDIR) $(WEBSITEDIR) && chmod -R og+rX $(WEBSITEDIR)

.phony: web
web: $(WEBSITEDIR)

distutils = $(PYTHON) ./setup.py -q $(1) --dist-dir=$(DISTDIR) $(2)
distutils_sdist = $(call distutils,sdist,--format=$(strip $(1)))
distutils_wininst = $(call distutils,bdist_wininst)

.PHONY: distfiles
distfiles:
	$(RM) MANIFEST
	$(call distutils_sdist, gztar)
	$(call distutils_sdist, bztar)
	$(call distutils_wininst)

.PHONY: dist
dist: $(WEBSITEDIR) distfiles
	cd $(WEBSITEDIR); tar jcf $(WEBDISTFILE) .
