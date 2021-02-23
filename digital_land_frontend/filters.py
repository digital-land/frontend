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
    DeveloperAgreementTypeMapper,
    DeveloperAgreementMapper,
)

from digital_land.specification import Specification


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


policy_to_doc_mapper = PolicyToDocMapper()


def policy_to_development_plan_filter(id):
    """
    Maps policy idenitifer to development plan document it is a part of

    E.g. astonclintonndp-B1 -> neigh-plan-buc-astonclintonndp
    """
    return policy_to_doc_mapper.get_name(id)


class MapperFilter:
    def __init__(self, mapper):
        self.mapper = mapper

    def filter(self, id, type="name"):
        if type == "url":
            return self.mapper.get_url(id)
        elif type == "slug":
            return self.mapper.get_slug(id)
        return self.mapper.get_name(id)


policy_mapper = MapperFilter(PolicyMapper())
policy_category_mapper = MapperFilter(PolicyCategoryMapper())
plan_type_mapper = MapperFilter(PlanTypeMapper())
dev_doc_mapper = MapperFilter(DevelopmentDocMapper())
developer_agreement_type_mapper = MapperFilter(DeveloperAgreementTypeMapper())
developer_agreement_mapper = MapperFilter(DeveloperAgreementMapper())


class MapperRouter:
    specification_path = "specification"

    def __init__(self, mappers):
        if len(mappers) == 0:
            raise ValueError("no mappers provided")
        self.mappers = mappers
        self.specification = self.load_specification()

    def load_specification(self):
        if os.path.isdir(self.specification_path):
            return Specification(self.specification_path)
        return None

    def dataset(self, fieldname):
        if self.specification is None:
            return fieldname
        parent = self.specification.field_parent(fieldname)
        return fieldname if parent == "category" else parent

    def route(self, k, fieldname, type="name"):
        dataset = self.dataset(fieldname)
        if dataset not in self.mappers:
            raise ValueError("no mapper found for dataset %s" % dataset)
        mapper = self.mappers[dataset]
        return mapper.filter(k, type)


category_mapper_router = MapperRouter(
    {
        "development-policy-category": policy_category_mapper,
        "development-plan-type": plan_type_mapper,
        "developer-agreement-type": developer_agreement_type_mapper,
    }
)


def strip_slug(s):
    parts = s.split("/")
    return parts[-1]


def is_list(v):
    """
    Check if variable is list
    """
    return isinstance(v, list)
