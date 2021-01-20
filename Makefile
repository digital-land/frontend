.PHONY: black black-check flake8 lint test

test:
	python -m pytest -vvs tests

black:
	black .

black-check:
	black --check .

flake8:
	flake8 --exclude .venv .

lint: black-check flake8
