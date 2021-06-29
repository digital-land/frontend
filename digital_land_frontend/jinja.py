import jinja2

from .filters import register_basic_filters, register_mapper_filters


def setup_jinja(view_model=None):
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
    env = jinja2.Environment(loader=multi_loader, autoescape=True)

    # register jinja filters
    register_basic_filters(env)
    register_mapper_filters(env, view_model)

    # set variables to make available to all templates
    env.globals["staticPath"] = "https://digital-land.github.io"

    return env
