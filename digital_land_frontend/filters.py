import os
import numbers
import validators
from jinja2 import evalcontextfilter, Markup

from .jinja_filters.mappers import (
    GeneralOrganisationMapper,
    GeographyMapper,
    PolicyMapper,
    DevelopmentDocMapper,
    PolicyToDocMapper,
    PlanTypeMapper,
    PolicyCategoryMapper,
)


def get_jinja_template_raw(template_file_path):
    if template_file_path:
        if os.path.exists(template_file_path):
            file = open(template_file_path, "r")
            return file.read()
    return None


@evalcontextfilter
def make_link(eval_ctx, url):
    """
    Converts a url string into an anchor element.

    Requires autoescaping option to be set to True
    """
    if url is not None:
        if validators.url(url):
            anchor = f'<a class="govuk-link" href="{url}">{url}</a>'
            if eval_ctx.autoescape:
                return Markup(anchor)
    return url


def is_valid_uri(uri):
    """
    Checks if a string is valid URI
    """
    if validators.url(uri):
        return True
    return False


def float_to_int(v):
    if v:
        return int(float(v))
    return ""


def commanum(v):
    """
    Makes large numbers readable by adding commas

    E.g. 1000000 -> 1,000,000
    """
    if isinstance(v, numbers.Number):
        return "{:,}".format(v)
    return v


def group_id_to_name_filter(id, group_type):
    if group_type == "organisation":
        return organisation_id_to_name_filter(id)
    else:
        raise NotImplementedError("group_type %s not implemented" % group_type)


organisation_mapper = GeneralOrganisationMapper()


def organisation_id_to_name_filter(id):
    """
    Maps organistion id to the name of the organisation

    E.g. local-authority-eng:HAG -> Harrogate Borough Council
    """
    return organisation_mapper.get_name(id)


def organisation_id_to_url_filter(id):
    """
    Maps organistion id to the url of the organisation

    E.g. local-authority-eng:HAG -> https://digital-land.github.io/organisation/local-authority-eng/HA"
    """
    return organisation_mapper.get_url(id)


geography_mapper = GeographyMapper()


def geography_to_name_filter(id):
    """
    Maps geography to name

    E.g. parish:E04001457 -> Aston Clinton
    """
    return geography_mapper.get_name(id)


def geography_to_url_filter(id):
    """
    Maps geograpahy to a link for the relevant geograpahy page

    E.g. parish:E04001457 -> https://digital-land.github.io/parish/E04001465/
    """
    return geography_mapper.get_url(id)


def geography_to_geometry_url_filter(id):
    """
    Maps geograpahy to a link for the relevant geometry geojson file

    E.g. parish:E04001457 -> https://digital-land.github.io/parish/E04001465/geometry.geojson
    """

    return geography_mapper.get_geometry_url(id)


policy_mapper = PolicyMapper()


def policy_mapper_filter(id, type="name"):
    """
    Maps policy idenitifer to policy name, url or slug

    E.g. bmwlp-P1 -> Safeguarding Mineral Resources
         worminghallndp-NH1 -> /development-policy/local-authority-eng/BUC/worminghallndp-NH1
         worminghallndp-NH1 -> https://digital-land.github.io/development-policy/local-authority-eng/BUC/worminghallndp-NH1
    """
    if type == "url":
        return policy_mapper.get_url(id)
    elif type == "slug":
        return policy_mapper.get_slug(id)
    return policy_mapper.get_name(id)


policy_to_doc_mapper = PolicyToDocMapper()


def policy_to_development_plan_filter(id):
    """
    Maps policy idenitifer to development plan document it is a part of

    E.g. astonclintonndp-B1 -> neigh-plan-buc-astonclintonndp
    """
    return policy_to_doc_mapper.get_name(id)


dev_doc_mapper = DevelopmentDocMapper()


def dev_doc_mapper_filter(id, type="name"):
    """
    Maps development plan document id to document name or url

    E.g. neigh-plan-buc-astonclintonndp -> Aston Clinton Neighbourhood Plan 2013-2033
    """
    if type == "url":
        return dev_doc_mapper.get_url(id)
    return dev_doc_mapper.get_name(id)


plan_type_mapper = PlanTypeMapper()


def plan_type_mapper_filter(id, type="name"):
    """
    Maps plan type ids to plan type names or urls

    E.g. local-plan -> Local plan
    """
    if type == "url":
        return plan_type_mapper.get_url(id)
    return plan_type_mapper.get_name(id)


class MapperFilter:
    def __init__(self, mapper):
        self.mapper = mapper

    def filter(self, id, type="name"):
        if type == "url":
            return self.mapper.get_url(id)
        elif type == "slug":
            return self.mapper.get_slug(id)
        return self.mapper.get_name(id)


policy_category_mapper = MapperFilter(PolicyCategoryMapper())


def strip_slug(s):
    parts = s.split("/")
    return parts[-1]


def is_list(v):
    """
    Check if variable is list
    """
    return isinstance(v, list)
