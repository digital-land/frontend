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

    def __init__(
        self,
        name,
        dataset,
        url_root=None,
        key_fields=["organisation", "site"],
        docs="docs",
    ):
        self.name = name
        self.dataset = dataset
        self.docs = Path(docs)
        self.key_fields = key_fields
        self.env = setup_jinja()
        self.index_template = self.env.get_template("index.html")
        self.row_template = self.env.get_template("row.html")

        if url_root:
            self.env.globals["urlRoot"] = url_root
        else:
            self.env.globals["urlRoot"] = f"/{name.replace(' ', '-')}/"

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
        self.slugs = set()
        rows = []
        for idx, row in enumerate(csv.DictReader(open(self.dataset)), start=1):
            if not row["slug"]:
                continue  # Skip rows without a unique slug

            row["slug"] = "/".join(
                row["slug"].split("/")[1:]
            )  # strip the prefix from slug

            output_dir = self.docs / row["slug"]
            if not output_dir.exists():
                output_dir.mkdir(parents=True)

            for field in self.geometry_fields:
                if field in row and row[field]:
                    self.create_geometry_file(output_dir, row, field)
                    row["has_geometry"] = True
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

        self.render(
            self.docs / "index.html",
            self.index_template,
            index=index,
            data_type=self.name,
        )

    @staticmethod
    def render(path, template, **kwargs):
        with open(path, "w") as f:
            logging.debug(f"creating {path}")
            f.write(template.render(**kwargs))

    def create_geometry_file(self, output_dir, row, field):
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
