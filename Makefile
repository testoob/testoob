PYTHON ?= python
DISTDIR = dist

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

DISTUTILS_SDIST_OPTIONS = --formats=bztar --dist-dir=../$(DISTDIR)
.PHONY: dist
dist:
	cd src; $(PYTHON) ./setup.py -q sdist $(DISTUTILS_SDIST_OPTIONS)
