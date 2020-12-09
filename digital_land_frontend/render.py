import csv
import json
import logging
import os
from collections import OrderedDict

import shapely.wkt

from digital_land_frontend.jinja import setup_jinja
from digital_land_frontend.jinja_filters.organisation_mapper import \
    OrganisationMapper


class Renderer:
    organisation_mapper = OrganisationMapper()

    def __init__(self, name, dataset, url_root=None, docs="docs"):
        self.name = name
        self.dataset = dataset
        self.docs = docs
        self.env = setup_jinja()
        self.index_template = self.env.get_template("index.html")
        self.row_template = self.env.get_template("row.html")
        self.ids = set()

        if url_root:
            self.env.globals["urlRoot"] = url_root
        else:
            self.env.globals["urlRoot"] = f"/{name.replace(' ', '-')}/"

    translations = str.maketrans({"/": "-", " ": "", "(": "", ")": "", "'": ""})

    def get_id(self, row, idx):
        id = row["site"].translate(self.translations)
        if not row["site"] or row["site"] in self.ids:
            id = f"{row['resource']}:{idx}"
        self.ids.add(id)
        return id

    def by_organisation(self, rows):
        by_organisation = {}
        by_organisation.setdefault(
            "no-organisation", {"name": "No organisation", "rows": []}
        )
        for row in rows:
            if row["organisation"]:
                o = {
                    "name": self.organisation_mapper.get_by_key(row["organisation"]),
                    "rows": [],
                }
                by_organisation.setdefault(row["organisation"], o)
                by_organisation[row["organisation"]]["rows"].append(row)
            else:
                by_organisation["no-organisation"]["rows"].append(row)

        result = OrderedDict(
            sorted(by_organisation.items(), key=lambda x: x[1]["name"])
        )
        result.move_to_end("no-organisation")
        return result

    def render_pages(self):
        self.ids = set()
        rows = []
        for idx, row in enumerate(csv.DictReader(open(self.dataset)), start=1):
            row["id"] = self.get_id(row, idx)
            self.create_geometry_file(row)
            self.render(
                f"{row['id']}/index.html",
                self.row_template,
                row=row,
                data_type=self.name,
            )
            rows.append(row)

        index = {
            "count": len(rows),
            "organisation": self.by_organisation(rows),
        }

        self.render("index.html", self.index_template, index=index, data_type=self.name)

    def render(self, path, template, **kwargs):
        path = os.path.join(self.docs, path)
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(path, "w") as f:
            logging.debug(f"creating {path}")
            f.write(template.render(**kwargs))

    def create_geometry_file(self, area):
        area_dir = f"{self.docs}/{area['id']}"
        if area["point"] == "POINT( )":
            return
        if not os.path.exists(area_dir):
            os.mkdir(area_dir)
        try:
            geojson = wkt_to_json_geometry(area["point"])
            with open(f"{area_dir}/geometry.geojson", "w") as f:
                json.dump(geojson, f)
        except Exception as e:
            print(e)


def wkt_to_json_geometry(input_):
    shape = shapely.wkt.loads(input_)
    return shapely.geometry.mapping(shape)
