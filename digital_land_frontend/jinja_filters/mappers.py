import csv
import logging

from ..caching import get


class Mapper:
    value_field = "name"
    key_filter = None

    def __init__(self):
        self.mapping = {}
        self.slug = {}
        self.loaded = False

    def load(self):
        for url in self.dataset_urls:
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
        return self.url_pattern.format(key=k, slug=slug)

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
    def all(self):
        return self.mapping


class OrganisationMapper(Mapper):
    dataset_urls = [
        "https://raw.githubusercontent.com/digital-land/organisation-dataset/master/collection/organisation.csv"
    ]
    key_field = "organisation"


class BaseGeometryMapper(Mapper):
    @Mapper.slug_to_key
    def get_geometry_url(self, k, slug=None):
        if k not in self.mapping:
            return None
        return self.geometry_url_pattern.format(key=k, slug=slug)


class ParishMapper(BaseGeometryMapper):
    dataset_urls = [
        "https://raw.githubusercontent.com/digital-land/parish-collection/main/dataset/parish.csv"
    ]
    key_field = "geography"
    url_pattern = "https://digital-land.github.io/parish/{key}"
    geometry_url_pattern = (
        "https://digital-land.github.io/parish/{key}/geometry.geojson"
    )

    def key_filter(self, k):
        return k.split(":")[-1]


class LocalAuthorityDistrictMapper(BaseGeometryMapper):
    dataset_urls = [
        "https://raw.githubusercontent.com/digital-land/local-authority-district-collection/main/dataset/local-authority-district.csv"
    ]
    key_field = "geography"
    value_field = "name"
    url_pattern = "https://digital-land.github.io/local-authority-district/{key}"
    geometry_url_pattern = "https://raw.githubusercontent.com/digital-land/local-authority-district/main/docs/{key}/geometry.geojson"

    def key_filter(self, k):
        return k.split(":")[-1]


class BoundaryMapper(BaseGeometryMapper):
    dataset_urls = [
        "https://raw.githubusercontent.com/digital-land/boundary-collection/master/index/parliamentary-boundary.csv",
    ]
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
        "https://raw.githubusercontent.com/digital-land/development-policy-area-collection/main/dataset/development-policy-area.csv"
    ]
    key_field = "development-policy-area"
    url_pattern = "https://digital-land.github.io{slug}"
    geometry_url_pattern = "https://digital-land.github.io{slug}/geometry.geojson"

    def get_name(self, slug):
        result = super().get_name(slug)
        if not result:
            return slug.split("/")[-1]
        return result


class GeographyMapper:
    def __init__(self):
        # self.registered_mappers = [ParishMapper(), DevelopmentPolicyAreaMapper(), BoundaryMapper()]
        self.parish_mapper = ParishMapper()
        self.dev_policy_area_mapper = DevelopmentPolicyAreaMapper()
        self.local_authority_district_mapper = LocalAuthorityDistrictMapper()
        self.boundary_mapper = BoundaryMapper()

    def _find_mappers(self, k):
        if k.startswith("/development-policy-area/"):
            return [self.dev_policy_area_mapper]
        elif k.startswith("/"):
            logging.warning("Unhandled geography key: %s", k)
            return []
        elif k.startswith("E04"):
            return [self.parish_mapper]
        else:
            return [self.local_authority_district_mapper, self.boundary_mapper]

    def with_mappers(func):
        def wrapped(self, k, *args, **kwargs):
            mappers = self._find_mappers(k)
            if not mappers:
                return ""
            return func(self, mappers, k, *args, **kwargs)

        return wrapped

    @with_mappers
    def _try_all_mappers(self, mappers, k, method):
        for mapper in mappers:
            func = getattr(mapper, method)
            result = func(k)
            if result:
                return result
        return None

    def get_name(self, k):
        return self._try_all_mappers(k, "get_name")

    def get_url(self, k):
        return self._try_all_mappers(k, "get_url")

    def get_geometry_url(self, k):
        return self._try_all_mappers(k, "get_geometry_url")
