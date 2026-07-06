PYTHON ?= python3

.PHONY: run test check reset-data

run:
	$(PYTHON) main.py

test:
	$(PYTHON) -m unittest discover -s tests -v

check:
	$(PYTHON) scripts/check_environment.py

reset-data:
	$(PYTHON) scripts/reset_data.py
