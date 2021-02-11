#!/usr/bin/env python
import jinja2

from digital_land_frontend.jinja_filters.mappers import GeneralOrganisationMapper


def setup_jinja():
    # register templates
    multi_loader = jinja2.ChoiceLoader(
        [
            jinja2.FileSystemLoader(searchpath="./src/templates"),
            jinja2.PrefixLoader(
                {
                    "digital-land-frontend": jinja2.FileSystemLoader(
                        searchpath="./digital_land_frontend/templates"
                    ),
                    "govuk-jinja-components": jinja2.PackageLoader(
                        "govuk_jinja_components"
                    ),
                }
            ),
        ]
    )
    env = jinja2.Environment(loader=multi_loader)

    return env


env = setup_jinja()
organisation_autocomplete_template = env.get_template("organisation-autocomplete.html")

# data for organisation autocomplete
organisation_mapper = GeneralOrganisationMapper()
orgs = [{"value": k, "text": v} for k, v in organisation_mapper.all().items()]


partials_dir = "digital_land_frontend/templates/partials"
with open(f"{partials_dir}/dl-organisation-autocomplete.html", "w") as f:
    f.write(organisation_autocomplete_template.render(orgs=orgs))
