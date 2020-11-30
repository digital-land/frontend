# Frontend

[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/psd/openregister/blob/master/LICENSE)

Frontend contains the code you need to start building a user interface for digital land pages and services. It builds on [GOV.UK frontend](https://github.com/alphagov/govuk-frontend).

## How to use digital-land-frontend

The easiest way to use digital-land-frontend is to install it with pip. We recommend working in a virtual environment.

You will also need to install the ported govuk templates.

To install both, run

    pip install -e git+https://github.com/digital-land/frontend.git#egg=digital_land_frontend
    pip install -e git+https://github.com/digital-land/govuk-jinja-components.git#egg=govuk_jinja_components

Then in your `render.py` or equivalent you'll need to register the templates (partials and macros) so that jinja knows they are available. You can do that with code similar to

    import jinja2
    
    # where you set up jinja add this
    multi_loader = jinja2.ChoiceLoader([
        jinja2.FileSystemLoader(searchpath="<<path to your templates>>"),
        jinja2.PrefixLoader({
            'govuk-jinja-components': jinja2.PackageLoader('govuk_jinja_components'),
            'digital-land-frontend': jinja2.PackageLoader('digital_land_frontend')
        })
    ])
    jinja2.Environment(loader=multi_loader)

Then in your templates you can access templates from `govuk-jinja-components` like this

    {% extends "govuk-jinja-components/template.html" %}

And from `digital-land-frontend` like this

    {% from "digital-land-frontend/components/page-feedback/macro.jinja" import dlfPageFeedback %}


### Compile latest stylesheets and javascript

Running

    gulp

will recompile the stylesheets and javascript files, as well as copying any vendor assets into the `digital_land_frontend/static` directory.

If you need to recompile the digital land **stylesheets**, run

    gulp stylesheets

If you need to recompile the digital land **javascripts**, run

    gulp js


### Update GOV.UK assets

Fecth the latest release of [GOV.UK frontend](https://github.com/alphagov/govuk-frontend) with

    npm update govuk-frontend

Once update it is recommended that you recompile the stylesheets.

    gulp stylesheets

### Contributing templates, partials and components

Check any HTML and jinja snippets with `curlylint`.

Install requirements.

    pip install -r requirements.txt

To check HTML run

    curlylint digital_land_frontend/templates/

### Working on the package locally

You should run

    pip install -e .

To make sure all the dependencies are installed