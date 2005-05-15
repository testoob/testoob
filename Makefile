PYTHON ?= python
all:
	@echo nothing to be done
test:
	$(PYTHON) ./tests/alltests.py
clean:
	$(RM) `find . -name "*~"`
	$(RM) `find . -name "*.pyc"`
.PHONY: all test clean
