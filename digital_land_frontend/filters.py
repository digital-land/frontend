import numbers
import os
from datetime import datetime

import validators
from digital_land.specification import Specification
from jinja2 import Markup, evalcontextfilter

from .jinja_filters.category_mappers import (
    ContributionFundingStatusMapper,
    ContributionPurposeMapper,
    DeveloperAgreementTypeMapper,
    DocumentTypeMapper,
    PlanTypeMapper,
    PolicyCategoryMapper,
)
from .jinja_filters.mappers import (
    DeveloperAgreementContributionMapper,
    DeveloperAgreementMapper,
    DevelopmentDocMapper,
    GeneralOrganisationMapper,
    GeographyMapper,
    PolicyMapper,
    PolicyToDocMapper,
)
from .jinja_filters.reference_mappers import ReferenceMapper


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


reference_mapper = ReferenceMapper()


def reference_filter(id, field):
    """
    Returns links to each entity that references the provided id in the provided field

    E.g.
    "article-4-document", "document-type" -> [
        {"reference": "article-4-document:CA05-1", "href": "/conservation-area/local-authority-eng/LBH/CA05", "text": "article-4-document:CA05-1"},
        {"reference": "article-4-document:CA11-2", "href": "/conservation-area/local-authority-eng/LBH/CA11", "text": "article-4-document:CA11-2"},
        ...
    ]
    """
    return reference_mapper.get_references(id, field)


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
doc_type_mapper = MapperFilter(DocumentTypeMapper())
developer_agreement_type_mapper = MapperFilter(DeveloperAgreementTypeMapper())
developer_agreement_mapper = MapperFilter(DeveloperAgreementMapper())
developer_agreement_contribution_mapper = MapperFilter(
    DeveloperAgreementContributionMapper()
)
contribution_purpose_mapper = MapperFilter(ContributionPurposeMapper())
contribution_funding_status_mapper = MapperFilter(ContributionFundingStatusMapper())


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
        # no specification
        if self.specification is None:
            return fieldname
        # fieldname not in set of fields
        if self.specification and fieldname not in self.specification.field.keys():
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
        "contribution-purpose": contribution_purpose_mapper,
        "contribution-funding-status": contribution_funding_status_mapper,
        "document-type": doc_type_mapper,
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


def is_historical(record):
    if not type(record) is dict:
        raise ValueError("record is not a dict")
    if "end-date" not in record.keys():
        raise ValueError("record does not contain end-date value")
    if record["end-date"] == "":
        return False
    today = datetime.now()

    if not record.get("end-date", None):
        return False

    end_date = datetime.strptime(record["end-date"], "%Y-%m-%d")
    return end_date < today


def contains_historical(lst):
    if not is_list(lst):
        raise ValueError("value provided is not a list")
    with_end_date = [i for i in lst if is_historical(i)]
    return len(with_end_date) > 0


def get_geometry_url_filter(record):
    if "geometry_url" in record and record["geometry_url"]:
        return record["geometry_url"]
    if "geographies" in record and record["geographies"]:
        return geography_to_geometry_url_filter(record["geographies"])
    if "statistical-geography" in record and record["statistical-geography"]:
        return geography_to_geometry_url_filter(record["statistical-geography"])
    return None


def key_field_filter(record, pipeline_name):
    specification_path = "specification"
    if os.path.isdir(specification_path):
        spec = Specification(specification_path)
        schema = spec.pipeline[pipeline_name]["schema"]
        key_field = spec.key_field(schema)
        return record.get(key_field)
    return None


def github_line_num_filter(n):
    return str(int(n) + 1)


def total_items_filter(obj):
    counts = [len(v) for k, v in obj.items()]
    return sum(counts)
