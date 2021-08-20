SOURCE_URL=https://raw.githubusercontent.com/digital-land/

# current git branch
BRANCH := $(shell git rev-parse --abbrev-ref HEAD)

.PHONY: black black-check flake8 lint test

all: lint test

init::
	pip install --upgrade pip setuptools
	pip install -e .
	pip install -r requirements.txt
	npm install


# update local copies of specification files
init::
	@mkdir -p specification/
	curl -qsL '$(SOURCE_URL)/specification/main/specification/dataset.csv' > specification/dataset.csv
	curl -qsL '$(SOURCE_URL)/specification/main/specification/dataset-schema.csv' > specification/dataset-schema.csv
	curl -qsL '$(SOURCE_URL)/specification/main/specification/schema.csv' > specification/schema.csv
	curl -qsL '$(SOURCE_URL)/specification/main/specification/schema-field.csv' > specification/schema-field.csv
	curl -qsL '$(SOURCE_URL)/specification/main/specification/field.csv' > specification/field.csv
	curl -qsL '$(SOURCE_URL)/specification/main/specification/datatype.csv' > specification/datatype.csv
	curl -qsL '$(SOURCE_URL)/specification/main/specification/typology.csv' > specification/typology.csv
	curl -qsL '$(SOURCE_URL)/specification/main/specification/pipeline.csv' > specification/pipeline.csv


test:
	python -m pytest -vvs tests

black:
	black .

black-check:
	black --check .

flake8:
	flake8 --exclude .venv,node_modules

lint: black-check flake8

js::
	gulp js

css::
	gulp stylesheets

assets:: js css

commit-assets::
	git add digital_land_frontend/static/stylesheets/
	git add digital_land_frontend/static/javascripts/
	git diff --quiet && git diff --staged --quiet || (git commit -m "Rebuilt frontend assets $(shell date +%F)"; git push origin $(BRANCH))
