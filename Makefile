all:
	@echo nothing to be done
test:
	./testing.py
clean:
	$(RM) *~ *.pyc
.PHONY: all test clean
