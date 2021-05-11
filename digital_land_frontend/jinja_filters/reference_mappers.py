import json
import logging

import requests
from digital_land.cli import SPECIFICATION

logger = logging.getLogger(__name__)


class ViewModelJsonQuery:
    def __init__(self, url_base="https://datasette-demo.digital-land.info/view_model/"):
        self.url_base = url_base

    def select(self, table, exact={}, joins=[], label=None, sort=None):
        url = f"{self.url_base}{table}.json"
        params = ["_shape=objects"]

        if label:
            params.append(f"_label={label}")

        if sort:
            params.append(f"_sort={sort}")

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
            if "rows" not in data:
                raise ValueError('no "rows" found in response:\n%s', data)

            if "expanded_columns" in data:
                row_iter = self.expand_columns(data)
            else:
                row_iter = data["rows"]

            try:
                url = response.links.get("next").get("url")
            except AttributeError:
                url = None
            yield from (
                {
                    key: value["label"] if isinstance(value, dict) else value
                    for key, value in row.items()
                }
                for row in row_iter
            )

    def expand_columns(self, data):
        col_map = {}
        for config, dest_col in data["expandable_columns"]:
            if config["column"] in data["expanded_columns"]:
                if dest_col in data["columns"]:
                    raise ValueError(f"name clash trying to expand {dest_col} label")
                col_map[config["column"]] = dest_col

        for row in data["rows"]:
            for src, dest in col_map.items():
                row[dest] = row[src]["label"]
                row[src] = row[src]["value"]
            yield row


class ReferenceMapper:
    relationships = {
        "geography": [
            ("document", "document_geography"),
            ("organisation", "organisation_geography"),
            ("policy", "policy_geography"),
        ],
        "category": [("document", "document_category"), ("policy", "policy_category")],
        "organisation": [
            ("document", "document_organisation"),
            ("geography", "organisation_geography"),
            ("policy", "policy_organisation"),
        ],
    }

    def __init__(self):
        self.view_model = ViewModelJsonQuery(
            "https://datasette-demo.digital-land.info/view_model/"
        )

    def get_references(self, value, field):
        field_typology = SPECIFICATION.field_typology(field)
        key = list(
            self.view_model.select(
                field_typology, exact={field_typology: value, "type": field}
            )
        )
        row_count = len(key)
        if row_count != 1:
            logger.warning(
                'select %s "%s" returned %s rows, expected exactly 1',
                field_typology,
                value,
                row_count,
            )
            return {}
        key_id = key[0]["id"]

        result = {}
        for type_, table in self.relationships[field_typology]:
            logger.info('looking in "%s" for "%s" relationships', table, type_)
            for row in self.view_model.select(
                type_,
                joins=[
                    {
                        "table": table,
                        "column": field_typology,
                        "value": key_id,
                    }
                ],
                label="slug_id",
                sort="name",
            ):
                result.setdefault(type_, []).append(
                    {
                        "id": row[type_],
                        "reference": row["reference"] or row[type_],
                        "href": row["slug"],
                        "text": row["name"],
                    }
                )

        return result
