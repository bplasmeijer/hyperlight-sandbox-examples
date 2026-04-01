VENV := .venv
PYTHON := $(VENV)/bin/python

.PHONY: all setup run clean

all: setup run

setup: $(PYTHON)

$(PYTHON):
	uv python install 3.12
	uv venv --python 3.12
	uv pip install "hyperlight-sandbox[wasm,python-guest]"

run: $(PYTHON)
	$(PYTHON) quickstart.py

clean:
	rm -rf $(VENV)
