import csv
import logging

from ..caching import get


class Mapper:
    value_field = "name"
    key_filter = None

    def __init__(self):
        self.mapping = {}
        self.slug = {}
        self.data_fetched = False

    def fetch_data(self):
        self.data_fetched = True
        return get(self.dataset_url)

    def create_mapping(self, data):
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
            if not self.data_fetched:
                data = self.fetch_data()
                self.create_mapping(data)
            return func(self, *args, **kwargs)

        return wrapped

    @lazy_load
    def get_by_key(self, k):
        return self.mapping.get(k)

    def slug_to_key(func):
        def wrapped(self, k, *args, **kwargs):
            if k.startswith("/"):
                k = k.split("/")[-1]
            return func(self, k, *args, **kwargs)

        return wrapped

    @lazy_load
    @slug_to_key
    def get_url(self, k):
        if k not in self.mapping:
            return None
        return self.url_pattern % k

    @slug_to_key
    def get_name(self, k):
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
    dataset_url = "https://raw.githubusercontent.com/digital-land/organisation-dataset/master/collection/organisation.csv"
    key_field = "organisation"


class BaseGeometryMapper(Mapper):
    @Mapper.slug_to_key
    def get_geometry_url(self, k):
        if k not in self.mapping:
            return None
        return self.geometry_url_pattern % k


class ParishMapper(BaseGeometryMapper):
    dataset_url = "https://raw.githubusercontent.com/digital-land/parish-collection/main/dataset/parish.csv"
    key_field = "geography"
    url_pattern = "https://digital-land.github.io/parish/%s"
    geometry_url_pattern = "https://digital-land.github.io/parish/%s/geometry.geojson"

    def key_filter(self, k):
        return k.split(":")[-1]


class BoundaryMapper(BaseGeometryMapper):
    dataset_url = "https://raw.githubusercontent.com/digital-land/boundary-collection/master/index/local-authority-boundary.csv"
    key_field = "statistical-geography"
    value_field = "boundary"
    url_pattern = "https://digital-land.github.io/organisation/local-authority-eng/%s"
    geometry_url_pattern = "https://github.com/digital-land/boundary-collection/blob/master/collection/local-authority/%s/index.geojson"

    def get_name(self, k):
        return None

    def get_url(self, k):
        return None  # This can be removed once we have pages for boundaries

    def get_geometry_url(self, k):
        super().get_name(k)


class DevelopmentPolicyAreaMapper(BaseGeometryMapper):
    dataset_url = "https://raw.githubusercontent.com/digital-land/development-policy-area-collection/main/dataset/development-policy-area.csv"
    key_field = "development-policy-area"
    url_pattern = "https://digital-land.github.io%s"
    geometry_url_pattern = "https://digital-land.github.io%s/geometry.geojson"

    def get_name(self, k):
        result = super().get_name(k)
        if not result:
            return k.split("/")[-1]
        return result


class GeographyMapper:
    def __init__(self):
        # self.registered_mappers = [ParishMapper(), DevelopmentPolicyAreaMapper(), BoundaryMapper()]
        self.parish_mapper = ParishMapper()
        self.dev_policy_area_mapper = DevelopmentPolicyAreaMapper()
        self.boundary_mapper = BoundaryMapper()

    def _find_mapper(self, k):
        if k.startswith("/development-policy-area/"):
            return self.dev_policy_area_mapper
        elif k.startswith("/"):
            logging.warning("Unhandled geography key: %s", k)
            return None
        elif k.startswith("E04"):
            return self.parish_mapper
        else:
            return self.boundary_mapper

    def with_mapper(func):
        def wrapped(self, k, *args, **kwargs):
            mapper = self._find_mapper(k)
            if not mapper:
                return ""
            return func(self, mapper, k, *args, **kwargs)

        return wrapped

    @with_mapper
    def get_name(self, mapper, k):
        return mapper.get_name(k)

    @with_mapper
    def get_url(self, mapper, k):
        return mapper.get_url(k)

    @with_mapper
    def get_geometry_url(self, mapper, k):
        return mapper.get_geometry_url(k)
