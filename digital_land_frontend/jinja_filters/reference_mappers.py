import json
import logging

import requests
from digital_land.cli import SPECIFICATION

logger = logging.getLogger(__name__)


class ViewModelJsonQuery:
    def __init__(self, url_base="https://datasette-demo.digital-land.info/view_model/"):
        self.url_base = url_base

    def select(self, table, exact={}, joins=[], label=None):
        url = f"{self.url_base}{table}.json"
        params = ["_shape=objects"]

        if label:
            params.append(f"_label={label}")

        for column, value in exact.items():
            params.append(f"{column}__exact={requests.utils.quote(value)}")

        for clause in joins:
            params.append(f"_through={requests.utils.quote(json.dumps(clause))}")

        param_string = "&".join(params)
        if param_string:
            url = f"{url}?{param_string}"

        return self.paginate(url)

    def get(self, url):
        try:
            response = requests.get(url)
        except ConnectionRefusedError:
            raise ConnectionError("failed to connect to view model api at %s" % url)
        return response

    def paginate(self, url):
        while url:
            response = self.get(url)
            data = response.json()
            try:
                url = response.links.get("next").get("url")
            except AttributeError:
                url = None
            yield from (
                {
                    key: value["label"] if isinstance(value, dict) else value
                    for key, value in row.items()
                }
                for row in data["rows"]
            )


class ReferenceMapper:
    def __init__(self):
        self.view_model = ViewModelJsonQuery("https://datasette-demo.digital-land.info/view_model/")

    def get_references(self, value, field):
        field_typology = SPECIFICATION.field_typology(field)
        key = list(
            self.view_model.select(field_typology, exact={field_typology: value, "type": field})
        )
        row_count = len(key)
        if row_count != 1:
            logger.warning(
                'select category "%s" returned %s rows, expected exactly 1',
                value,
                row_count,
            )
            return None
        key_id = key[0]["id"]
        schemas = SPECIFICATION.schema_from.get(field, [])
        for schema in schemas:
            typology = SPECIFICATION.field_typology(schema)

            for row in self.view_model.select(
                typology,
                joins=[
                    {
                        "table": f"{typology}_{field_typology}",
                        "column": field_typology,
                        "value": key_id,
                    },
                ],
                label="slug_id",
            ):
                yield {
                    "reference": row["reference"] or row[typology],
                    "href": row["slug_id"],
                    "text": row["name"],
                }
