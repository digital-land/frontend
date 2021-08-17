import csv
import logging
import re
import sys

from ..caching import get

csv.field_size_limit(sys.maxsize)


class Mapper:
    value_field = "name"
    key_filter = None

    def __init__(self):
        self.mapping = {}
        self.slug = {}
        self.to_slug_mapping = {}
        self.loaded = False

    def load(self):
        for url in self.dataset_urls:
            logging.debug("mapping data for %s", url)
            self.map_data(self.fetch_data(url))

    def fetch_data(self, url):
        self.loaded = True
        return get(url)

    def map_data(self, data):
        cr = csv.DictReader(data.splitlines())
        for row in cr:
            key = row[self.key_field]
            if self.key_filter:
                key = self.key_filter(key)
            self.mapping[key] = row[self.value_field]

            if row.get("slug", None):
                self.slug[row["slug"]] = row[self.value_field]
                self.to_slug_mapping[key] = row["slug"]

    def lazy_load(func):
        def wrapped(self, *args, **kwargs):
            if not self.loaded:
                self.load()
            return func(self, *args, **kwargs)

        return wrapped

    @lazy_load
    def get_by_key(self, k):
        return self.mapping.get(k)

    def slug_to_key(func):
        def wrapped(self, k, *args, **kwargs):
            if k.startswith("/"):
                kwargs["slug"] = k
                k = k.split("/")[-1]
            return func(self, k, *args, **kwargs)

        return wrapped

    @lazy_load
    @slug_to_key
    def get_url(self, k, slug=None):
        if k not in self.mapping:
            return None
        return self.url_pattern.format(key=k.replace(":", "/"), slug=slug)

    @slug_to_key
    def get_name(self, k, slug=None):
        return self.get_by_key(k)

    @lazy_load
    def get_mapping(self):
        return self.mapping

    @lazy_load
    def replace_key(self, current, replacement):
        if current in self.mapping:
            self.mapping[replacement] = self.mapping[current]
            del self.mapping[current]

    @lazy_load
    def get_slug(self, k):
        return self.to_slug_mapping.get(k)

    @lazy_load
    def all(self):
        return self.mapping


class GeneralMapper:
    def __init__(self):
        if len(self.mappers) == 0:
            raise ValueError("no mappers")

    def match_mapper(func):
        def wrapped(self, k):
            matched = False
            for mapper in self.mappers:
                if mapper.matcher.match(k):
                    matched = True
                    result = func(self, mapper, k)
                    if result:
                        return result

            if not matched:
                raise ValueError("no mapper found for key %s" % k)
            return None

        return wrapped

    @match_mapper
    def get_name(self, mapper, k):
        return mapper.get_name(k)

    @match_mapper
    def get_url(self, mapper, k):
        return mapper.get_url(k)


class OrganisationMapper(Mapper):
    dataset_urls = [
        "https://raw.githubusercontent.com/digital-land/organisation-dataset/master/collection/organisation.csv"
    ]
    url_pattern = "https://digital-land.github.io/organisation/{key}"
    key_field = "organisation"
    matcher = re.compile(r"^.*")


class NeighbourhoodPlanAreaMapper(Mapper):
    dataset_urls = [
        "https://collection-dataset.s3.eu-west-2.amazonaws.com/neighbourhood-plan-area-collection/dataset/neighbourhood-plan-area.csv"
    ]
    url_pattern = "https://digital-land.github.io/{key}"
    key_field = "organisation"
    matcher = re.compile(r"^neighbourhood-plan-area:")


class GeneralOrganisationMapper(GeneralMapper):
    organisations = OrganisationMapper()
    neighbourhood_plan_areas = NeighbourhoodPlanAreaMapper()
    mappers = [neighbourhood_plan_areas, organisations]


class PolicyMapper(Mapper):
    dataset_urls = [
        "https://collection-dataset.s3.eu-west-2.amazonaws.com/development-policy-collection/dataset/development-policy.csv"
    ]
    key_field = "development-policy"
    url_pattern = "https://digital-land.github.io{slug}"

    def get_url(self, k):
        return super().get_url(k, self.get_slug(k))


class DevelopmentDocMapper(Mapper):
    dataset_urls = [
        "https://collection-dataset.s3.eu-west-2.amazonaws.com/development-plan-document-collection/dataset/development-plan-document.csv"
    ]
    key_field = "development-plan-document"
    url_pattern = "https://digital-land.github.io{slug}"

    def get_url(self, k):
        return super().get_url(k, self.get_slug(k))


class PolicyToDocMapper(Mapper):
    dataset_urls = [
        "https://raw.githubusercontent.com/digital-land/slug-index/main/index/policy-to-doc-index.csv"
    ]
    key_field = "development-policy"
    value_field = "development-plan-document"


class DeveloperAgreementMapper(Mapper):
    dataset_urls = [
        "https://collection-dataset.s3.eu-west-2.amazonaws.com/developer-contributions-collection/dataset/developer-agreement.csv"
    ]
    key_field = "developer-agreement"
    url_pattern = "https://digital-land.github.io{slug}"
    value_field = "planning-application"  # developer agreements don't have a name field

    def get_url(self, k):
        return super().get_url(k, self.get_slug(k))


class DeveloperAgreementContributionMapper(Mapper):
    dataset_urls = [
        "https://collection-dataset.s3.eu-west-2.amazonaws.com/developer-contributions-collection/dataset/developer-agreement-contribution.csv"
    ]
    key_field = "developer-agreement-contribution"
    url_pattern = "https://digital-land.github.io{slug}"
    value_field = "developer-agreement-contribution"  # developer agreement contributions don't have a name field

    def get_url(self, k):
        return super().get_url(k, self.get_slug(k))


class BaseGeometryMapper(Mapper):
    key_field = "geography"

    @Mapper.lazy_load
    @Mapper.slug_to_key
    def get_geometry_url(self, k, slug=None):
        if k not in self.mapping:
            return None
        return self.geometry_url_pattern.format(key=k, slug=slug)


class ParishMapper(BaseGeometryMapper):
    dataset_urls = [
        "https://collection-dataset.s3.eu-west-2.amazonaws.com/parish-collection/dataset/parish.csv"
    ]
    matcher = re.compile(r"^E04")
    key_field = "geography"
    url_pattern = "https://digital-land.github.io/parish/{key}"
    geometry_url_pattern = (
        "https://digital-land.github.io/parish/{key}/geometry.geojson"
    )

    def key_filter(self, k):
        return k.split(":")[-1]


class LocalAuthorityDistrictMapper(BaseGeometryMapper):
    dataset_urls = [
        "https://collection-dataset.s3.eu-west-2.amazonaws.com/local-authority-district-collection/dataset/local-authority-district.csv"
    ]
    matcher = re.compile(r"")
    value_field = "name"
    url_pattern = "https://digital-land.github.io/local-authority-district/{key}"
    geometry_url_pattern = "https://raw.githubusercontent.com/digital-land/local-authority-district/main/docs/{key}/geometry.geojson"

    def key_filter(self, k):
        return k.split(":")[-1]


class BoundaryMapper(BaseGeometryMapper):
    dataset_urls = [
        "https://raw.githubusercontent.com/digital-land/boundary-collection/master/index/parliamentary-boundary.csv",
    ]
    matcher = re.compile(r"")
    key_field = "statistical-geography"
    value_field = "boundary"
    url_pattern = (
        "https://digital-land.github.io/organisation/local-authority-eng/{key}"
    )
    geometry_url_pattern = "https://github.com/digital-land/boundary-collection/blob/master/collection/local-authority/{key}/index.geojson"

    def get_name(self, k):
        return None

    def get_url(self, k):
        return None  # This can be removed once we have pages for boundaries

    def get_geometry_url(self, k):
        return super().get_name(k)


class DevelopmentPolicyAreaMapper(BaseGeometryMapper):
    dataset_urls = [
        "https://collection-dataset.s3.eu-west-2.amazonaws.com/development-policy-area-collection/dataset/development-policy-area.csv"
    ]
    matcher = re.compile(r"^/development-policy-area/")
    url_pattern = "https://digital-land.github.io{slug}"
    geometry_url_pattern = "https://digital-land.github.io{slug}/geometry.geojson"

    def get_name(self, slug):
        result = super().get_name(slug)
        if not result:
            return slug.split("/")[-1]
        return result


class ConservationAreaMapper(BaseGeometryMapper):
    dataset_urls = [
        "https://collection-dataset.s3.eu-west-2.amazonaws.com/conservation-area-collection/dataset/conservation-area.csv"
    ]
    key_field = "slug"
    matcher = re.compile(r"^/conservation-area/")
    url_pattern = "https://digital-land.github.io{slug}"
    geometry_url_pattern = "https://digital-land.github.io{slug}/geometry.geojson"

    def get_name(self, slug):
        return self.mapping.get(slug, None)

    def get_url(self, slug):
        if slug not in self.slug:
            return None
        return self.url_pattern.format(slug=slug)

    @Mapper.lazy_load
    def get_geometry_url(self, slug):
        if slug not in self.slug:
            return None
        return self.geometry_url_pattern.format(slug=slug)


class GeographyMapper(GeneralMapper):
    mappers = [
        ParishMapper(),
        DevelopmentPolicyAreaMapper(),
        ConservationAreaMapper(),
        LocalAuthorityDistrictMapper(),
        BoundaryMapper(),
    ]

    @GeneralMapper.match_mapper
    def get_geometry_url(self, mapper, k):
        return mapper.get_geometry_url(k)
