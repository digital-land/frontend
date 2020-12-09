import csv
import json
import logging
from collections import OrderedDict
from pathlib import Path

import shapely.wkt

from digital_land_frontend.jinja import setup_jinja
from digital_land_frontend.jinja_filters.organisation_mapper import OrganisationMapper


class Renderer:
    organisation_mapper = OrganisationMapper()
    translations = str.maketrans({"/": "-", " ": "", "(": "", ")": "", "'": ""})
    geometry_fields = ["geometry", "point"]

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

    def get_id(self, row, idx):
        id_ = row["site"].translate(self.translations)
        if not row["site"] or row["site"].lower() in self.ids:
            id_ = f"{row['resource']}:{idx}"
        self.ids.add(id_.lower())
        return id_

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
            output_dir = Path(self.docs, row["id"])
            if not output_dir.exists():
                output_dir.mkdir()

            for field in self.geometry_fields:
                if field in row and row[field]:
                    self.create_geometry_file(output_dir, row, field)
                    break

            self.render(
                output_dir / "index.html",
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
        with open(path, "w") as f:
            logging.debug(f"creating {path}")
            f.write(template.render(**kwargs))

    def create_geometry_file(self, output_dir, row, field):
        # Remove this once dataset is fixed
        if row[field] == "POINT( )":
            return

        try:
            geojson = {"type": "Feature"}
            geojson["geometry"] = wkt_to_json_geometry(row[field])
            geojson["properties"] = row
            with open(output_dir / "geometry.geojson", "w") as f:
                json.dump(geojson, f)
        except Exception as e:
            logging.exception(e)


def wkt_to_json_geometry(input_):
    shape = shapely.wkt.loads(input_)
    return shapely.geometry.mapping(shape)
