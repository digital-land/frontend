import jinja2

from .filters import (
    category_mapper_router,
    contains_historical,
    dev_doc_mapper,
    developer_agreement_contribution_mapper,
    developer_agreement_mapper,
    developer_agreement_type_mapper,
    geography_to_geometry_url_filter,
    geography_to_name_filter,
    geography_to_url_filter,
    get_geometry_url_filter,
    github_line_num_filter,
    group_id_to_name_filter,
    is_historical,
    is_list,
    key_field_filter,
    make_link,
    organisation_id_to_name_filter,
    organisation_id_to_url_filter,
    plan_type_mapper,
    policy_category_mapper,
    policy_mapper,
    policy_to_development_plan_filter,
    reference_filter,
    strip_slug,
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
    env.filters["organisation_id_to_url"] = organisation_id_to_url_filter
    env.filters["geography_to_name"] = geography_to_name_filter
    env.filters["geography_to_url"] = geography_to_url_filter
    env.filters["geography_to_geometry_url"] = geography_to_geometry_url_filter
    env.filters["clean_slug"] = strip_slug
    env.filters["make_link"] = make_link
    env.filters["is_list"] = is_list
    env.filters["is_historical"] = is_historical
    env.filters["contains_historical"] = contains_historical
    env.filters["get_geometry_url"] = get_geometry_url_filter
    env.filters["policy_to_development_plan"] = policy_to_development_plan_filter
    env.filters["policy_mapper"] = policy_mapper.filter
    env.filters["dev_doc_mapper"] = dev_doc_mapper.filter
    env.filters["plan_type_mapper"] = plan_type_mapper.filter
    env.filters["policy_category_mapper"] = policy_category_mapper.filter
    env.filters["developer_agreement_mapper"] = developer_agreement_mapper.filter
    env.filters[
        "developer_agreement_contribution_mapper"
    ] = developer_agreement_contribution_mapper.filter
    env.filters[
        "developer_agreement_type_mapper"
    ] = developer_agreement_type_mapper.filter
    env.filters["dl_category_mapper"] = category_mapper_router.route
    env.filters["key_field"] = key_field_filter
    env.filters["github_line_num"] = github_line_num_filter
    env.filters["reference_mapper"] = reference_filter

    # set variables to make available to all templates
    env.globals["staticPath"] = "https://digital-land.github.io"

    return env
