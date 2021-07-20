import functools
import logging
import numbers
import os
from collections import Mapping
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

logger = logging.getLogger(__name__)


def register_basic_filters(env):
    env.filters["clean_slug"] = strip_slug
    env.filters["make_link"] = make_link
    env.filters["is_list"] = is_list
    env.filters["is_historical"] = is_historical
    env.filters["contains_historical"] = contains_historical
    env.filters["key_field"] = key_field_filter
    env.filters["github_line_num"] = github_line_num_filter
    env.filters["total_items"] = total_items_filter
    env.filters["split_to_list"] = split_to_list


def register_mapper_filters(env, view_model=None):
    contribution_funding_status_mapper = MapperFilter(ContributionFundingStatusMapper())
    contribution_purpose_mapper = MapperFilter(ContributionPurposeMapper())
    developer_agreement_contribution_mapper = MapperFilter(
        DeveloperAgreementContributionMapper()
    )
    developer_agreement_mapper = MapperFilter(DeveloperAgreementMapper())
    developer_agreement_type_mapper = MapperFilter(DeveloperAgreementTypeMapper())
    doc_type_mapper = MapperFilter(DocumentTypeMapper())
    geography_mapper = GeographyMapper()
    organisation_mapper = GeneralOrganisationMapper()
    plan_type_mapper = MapperFilter(PlanTypeMapper())
    policy_category_mapper = MapperFilter(PolicyCategoryMapper())
    policy_to_doc_mapper = PolicyToDocMapper()

    env.filters["dev_doc_mapper"] = MapperFilter(DevelopmentDocMapper()).filter
    env.filters[
        "developer_agreement_contribution_mapper"
    ] = developer_agreement_contribution_mapper.filter
    env.filters["developer_agreement_mapper"] = developer_agreement_mapper.filter
    env.filters[
        "developer_agreement_type_mapper"
    ] = developer_agreement_type_mapper.filter
    env.filters["geography_to_geometry_url"] = geography_mapper.get_geometry_url
    env.filters["geography_to_name"] = geography_mapper.get_name
    env.filters["geography_to_url"] = geography_mapper.get_url
    env.filters["get_geometry_url"] = functools.partial(
        get_geometry_url_filter, geography_mapper
    )
    env.filters["group_id_to_name"] = functools.partial(
        group_id_to_name_filter, organisation_mapper
    )
    env.filters["organisation_id_to_name"] = organisation_mapper.get_name
    env.filters["organisation_id_to_url"] = organisation_mapper.get_url
    env.filters["plan_type_mapper"] = plan_type_mapper.filter
    env.filters["policy_category_mapper"] = policy_category_mapper.filter
    env.filters["policy_mapper"] = MapperFilter(PolicyMapper()).filter
    env.filters["policy_to_development_plan"] = policy_to_doc_mapper.get_name

    env.filters["dl_category_mapper"] = MapperRouter(
        {
            "development-policy-category": policy_category_mapper,
            "development-plan-type": plan_type_mapper,
            "developer-agreement-type": developer_agreement_type_mapper,
            "contribution-purpose": contribution_purpose_mapper,
            "contribution-funding-status": contribution_funding_status_mapper,
            "document-type": doc_type_mapper,
        }
    ).route

    if view_model:
        env.filters["reference_mapper"] = ReferenceMapper(view_model).get_references
    else:
        # provide a no-op function to stop jinja complaining
        env.filters["reference_mapper"] = lambda x: x


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


def group_id_to_name_filter(organisation_mapper, id, group_type):
    if group_type == "organisation":
        return organisation_mapper.get_name(id)
    else:
        raise NotImplementedError("group_type %s not implemented" % group_type)


class MapperFilter:
    def __init__(self, mapper):
        self.mapper = mapper

    def filter(self, id, type="name"):
        if type == "url":
            return self.mapper.get_url(id)
        elif type == "slug":
            return self.mapper.get_slug(id)
        return self.mapper.get_name(id)


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


def get_geometry_url_filter(geography_mapper, record):
    if "geometry_url" in record and record["geometry_url"]:
        return record["geometry_url"]
    if "geographies" in record and record["geographies"]:
        return geography_mapper.get_geometry_url(record["geographies"])
    if "statistical-geography" in record and record["statistical-geography"]:
        return geography_mapper.get_geometry_url(record["statistical-geography"])
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
    if isinstance(obj, Mapping):
        counts = [len(v) for k, v in obj.items()]
        return sum(counts)

    logger.error(f"total_items expected a Dict. But got {type(obj)}")
    return None


def split_to_list(s):
    return s.split(";")


def hex_to_rgb_string_filter(hex):
    """
    Given hex will return rgb string

    E.g. #0b0c0c ==> "11, 12, 12"
    """
    h = hex.lstrip("#")
    rgb = tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))
    return f"{rgb[0]},{rgb[1]},{rgb[2]}"
