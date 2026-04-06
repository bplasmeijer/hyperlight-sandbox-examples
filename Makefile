VENV := .venv
PYTHON := $(VENV)/bin/python
PYTHONPATH_SRC := src

.PHONY: all setup run run-real run-fn run-hf run-hf-llm clean

all: setup run

setup: $(PYTHON)

$(PYTHON):
	uv sync

run: $(PYTHON)
	PYTHONPATH=$(PYTHONPATH_SRC) $(PYTHON) examples/quickstart.py

run-real: $(PYTHON)
	PYTHONPATH=$(PYTHONPATH_SRC) $(PYTHON) examples/real_example.py

run-fn: $(PYTHON)
	PYTHONPATH=$(PYTHONPATH_SRC) $(PYTHON) examples/function_call_example.py

run-hf: $(PYTHON)
	PYTHONPATH=$(PYTHONPATH_SRC) $(PYTHON) examples/huggingface_example.py

run-hf-llm: $(PYTHON)
	PYTHONPATH=$(PYTHONPATH_SRC) $(PYTHON) examples/hf_llm_example.py

clean:
	rm -rf $(VENV)
