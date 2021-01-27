.PHONY: black black-check flake8 lint test

all: lint test

init:
	pip install --upgrade pip setuptools
	pip install -e .
	pip install -r requirements.txt

test:
	python -m pytest -vvs tests

black:
	black .

black-check:
	black --check .

flake8:
	flake8 --exclude==.venv,node_modules .

lint: black-check flake8
