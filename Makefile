.RECIPEPREFIX := >
.PHONY: setup lint format test demo run

# Repo-local Matplotlib config (portable)
export MPLCONFIGDIR := $(CURDIR)/data/cache/matplotlib

# --- Cross-platform Python/venv detection (no uname needed) ---
ifeq ($(OS),Windows_NT)
PY  := .venv/Scripts/python.exe
PIP := .venv/Scripts/python.exe -m pip
# Portable "mkdir -p" via Python (works on Windows)
MKDIR_P = $(PY) -c "import os,sys; os.makedirs(sys.argv[1], exist_ok=True)"
else
PY  := .venv/bin/python
PIP := .venv/bin/pip
# On Unix we can use mkdir -p
MKDIR_P = mkdir -p
endif

setup:
> python -m venv .venv
> $(PY) -m pip install -U pip
> $(PIP) install -e .[dev]

lint:
> $(PY) -m ruff check src tests
> $(PY) -m black --check src tests

format:
> $(PY) -m black src tests
> $(PY) -m ruff check --fix src tests

test:
> $(PY) -m pytest -q --maxfail=1 --disable-warnings --cov=expab

demo:
> $(MKDIR_P) "$(MPLCONFIGDIR)"
> $(PY) -m expab.cli simulate --n-users 50000 --exp-id signup_v1 --base-conv 0.28 --lift 0.02 --seed 42 --segments device,geo --out data/processed/signup_v1/
> $(PY) -m expab.cli analyze --input data/processed/signup_v1/ --metric completed_profile --cuped --segments device,geo --out reports/signup_v1/
> $(PY) -m expab.cli report --results reports/signup_v1/

run: demo
