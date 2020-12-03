import jinja2

from .filters import organisation_id_to_name_filter


def setup_jinja():
    # register templates
    multi_loader = jinja2.ChoiceLoader(
        [
            jinja2.FileSystemLoader(searchpath=["./templates"]),
            jinja2.PrefixLoader(
                {
                    "govuk-jinja-components": jinja2.PackageLoader(
                        "govuk_jinja_components"
                    ),
                    "digital-land-frontend": jinja2.PackageLoader(
                        "digital_land_frontend"
                    ),
                }
            ),
        ]
    )
    env = jinja2.Environment(loader=multi_loader)

    # register jinja filters
    env.filters["organisation_id_to_name"] = organisation_id_to_name_filter

    # set variables to make available to all templates
    env.globals["staticPath"] = "https://digital-land.github.io"

    return env
