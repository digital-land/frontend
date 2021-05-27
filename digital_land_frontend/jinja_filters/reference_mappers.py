import json
import logging
import time

import requests
from digital_land.cli import SPECIFICATION

logger = logging.getLogger(__name__)


class ViewModelJsonQuery:
    def __init__(self, url_base="https://datasette-demo.digital-land.info/view_model/"):
        self.url_base = url_base

    def get_id(self, table, value):
        url = f"{self.url_base}get_{table}_id.json"
        params = ["_shape=objects",
                  f"{table}={value}"]

        url = f"{url}?{'&'.join(params)}"
        return self.paginate(url)

    def get_references_by_id(self, table, id):
        url = f"{self.url_base}get_{table}_references.json"
        params = ["_shape=objects",
                  f"{table}={id}"]

        url = f"{url}?{'&'.join(params)}"
        return self.paginate(url)


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
            start_time = time.time()
            response = self.get(url)
            logger.info("request time: %.2fs, %s", time.time() - start_time, url)
            try:
                data = response.json()
            except Exception as e:
                logger.error(
                    "json not found in response (url: %s):\n%s", url, response.content
                )
                raise e

            if "rows" not in data:
                logger.warning("url: %s", url)
                raise ValueError('no "rows" found in response:\n%s', data)

            if "expanded_columns" in data:
                row_iter = self.expand_columns(data)
            else:
                row_iter = data["rows"]

            try:
                url = response.links.get("next").get("url")
            except AttributeError:
                url = None

            yield from row_iter

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
    xref_datasets = {
        "geography",
        "category",
        "policy",
        "document"
    }

    def __init__(self):
        self.view_model = ViewModelJsonQuery(
            "https://datasette-demo.digital-land.info/view_model/"
        )

    def get_references(self, value, field):
        field_typology = SPECIFICATION.field_typology(field)
        if field_typology not in self.xref_datasets:
            logger.info("no relationships configured for %s typology", field_typology)
            return {}

        key = list(
            self.view_model.get_id(field_typology, value)
        )

        if key and "type" in key[0]:
            key = [id for id in key if id["type"] == field]

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
        logger.debug('looking for "%s" relationships', field_typology)

        for row in self.view_model.get_references_by_id(field_typology, key_id):
            result.setdefault(row["type"], []).append(
                {
                    "id": row["id"],
                    "reference": row["reference"],
                    "href": row["href"],
                    "text": row["name"],
                }
            )

        return result
