import jinja2

from .filters import (
    group_id_to_name_filter,
    organisation_id_to_name_filter,
    geography_to_name_filter,
    geography_to_url_filter,
    geography_to_geometry_url_filter,
    policy_mapper_filter,
    strip_slug,
    make_link,
    is_list,
    policy_to_development_plan_filter,
    dev_doc_mapper_filter,
    plan_type_mapper_filter,
)


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
    env = jinja2.Environment(loader=multi_loader, autoescape=True)

    # register jinja filters
    env.filters["group_id_to_name"] = group_id_to_name_filter
    env.filters["organisation_id_to_name"] = organisation_id_to_name_filter
    env.filters["geography_to_name"] = geography_to_name_filter
    env.filters["geography_to_url"] = geography_to_url_filter
    env.filters["geography_to_geometry_url"] = geography_to_geometry_url_filter
    env.filters["policy_mapper"] = policy_mapper_filter
    env.filters["clean_slug"] = strip_slug
    env.filters["make_link"] = make_link
    env.filters["is_list"] = is_list
    env.filters["policy_to_development_plan"] = policy_to_development_plan_filter
    env.filters["dev_doc_mapper"] = dev_doc_mapper_filter
    env.filters["plan_type_mapper"] = plan_type_mapper_filter

    # set variables to make available to all templates
    env.globals["staticPath"] = "https://digital-land.github.io"

    return env
