import csv
import json
import logging
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

import requests
import shapely.wkt

from digital_land_frontend.jinja import setup_jinja
from digital_land_frontend.jinja_filters.mappers import (
    GeographyMapper,
    OrganisationMapper,
)


class Renderer:
    organisation_mapper = OrganisationMapper()
    geography_mapper = GeographyMapper()
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
        self.index = defaultdict(lambda: {"count": 0, "references": set(), "items": []})
        self.index_template = self.env.get_template("index.html")
        self.generic_index_template = self.env.get_template("generic_index.html")
        self.row_template = self.env.get_template("row.html")

        if url_root:
            self.env.globals["urlRoot"] = url_root
        else:
            self.env.globals["urlRoot"] = f"/{name.replace(' ', '-')}/"

    def by_organisation(self, rows):
        by_organisation = {}
        for row in rows:
            if row["organisation"]:
                o = {
                    "name": self.organisation_mapper.get_by_key(row["organisation"]),
                    "items": [],
                }
                by_organisation.setdefault(row["organisation"], o)
                by_organisation[row["organisation"]]["items"].append(row)
            else:
                by_organisation["no-organisation"]["items"].append(row)

        result = OrderedDict(
            sorted(by_organisation.items(), key=lambda x: x[1]["name"])
        )

        if "no-organisation" in result:
            result["no-organisation"]["name"] = "No organisation"
            result.move_to_end("no-organisation")

        return result

    def render_pages(self):
        self.slugs = set()
        rows = []
        for idx, row in enumerate(csv.DictReader(open(self.dataset)), start=1):
            if not row["slug"]:
                continue  # skip rows without a unique slug

            if row["slug"] in self.slugs:
                logging.warning("Duplicate slug found: %s", row["slug"])

            breadcrumb = slug_to_breadcrumb(row["slug"])

            row["href"] = "/".join(
                row["slug"].split("/")[2:]
            )  # strip the prefix from slug

            output_dir = self.docs / row["href"]
            if not output_dir.exists():
                output_dir.mkdir(parents=True)

            for field in self.geometry_fields:
                if field in row and row[field]:
                    create_geometry_file(output_dir, row, field)
                    row["geometry_url"] = "geometry.geojson"
                    break

            self.render(
                output_dir / "index.html",
                self.row_template,
                row=row,
                data_type=self.name,
                breadcrumb=breadcrumb,
            )
            rows.append(row)
            self.add_to_index(row["slug"], row)
            self.slugs.add(row["slug"])

        self.index[""] = {
            "count": len(rows),
            "groups": self.by_organisation(rows),
            "group_type": "organisation",
        }

        self.render_index_pages()

    def add_to_index(self, slug, row):
        _, __, stem = slug.split("/", 2)
        self._add_to_index(stem, row)

    def _add_to_index(self, slug, row=None):
        if slug.find("/") <= 0:
            # no more parts of the path to index
            return

        stem, name = slug.rsplit("/", 1)
        if name in self.index[stem]["references"]:
            return
        self.index[stem]["references"].add(name)
        self.index[stem]["count"] += 1
        index_entry = {
            "reference": format_name(name) if not row else name,
            "href": slug_to_relative_path(slug, strip_prefix=stem),
        }
        if row:
            index_entry["text"] = row["name"]
        self.index[stem]["items"].append(index_entry)
        self._add_to_index(stem)

    def render_index_pages(self):
        for path, i in self.index.items():
            if path:
                slug = f"/{self.name}/{path}"
            else:
                slug = f"/{self.name}"
            self.render(
                self.docs / path / "index.html",
                self.index_template if path == "" else self.generic_index_template,
                index=i,
                data_type=self.name,
                breadcrumb=slug_to_breadcrumb(slug),
            )

    @staticmethod
    def render(path, template, **kwargs):
        with open(path, "w") as f:
            logging.debug(f"creating {path}")
            f.write(template.render(**kwargs))


re_all_upper = re.compile(r"^[A-Z]*$")
re_strip = re.compile(r"[^a-zA-Z]")


def format_name(name):
    if re_all_upper.match(name):
        return name
    return re_strip.sub(" ", name).title()


def slug_to_breadcrumb(slug):
    logging.debug(">> slug_to_breadcumb(%s)", slug)
    next_relative_path = "../"
    breadcrumb = []
    first_item = True
    for part in slug.split("/")[-1:0:-1]:
        if first_item:
            text = part
        else:
            text = format_name(part)

        entry = {"text": text}
        if first_item:
            first_item = False
        else:
            entry["href"] = next_relative_path
            next_relative_path += "../"

        breadcrumb.append(entry)

    breadcrumb.reverse()
    logging.debug("<< (%s)", breadcrumb)
    return breadcrumb


def slug_to_relative_path(slug, strip_prefix=None):
    logging.debug(">> slug_to_relative_path(%s, %s)", slug, strip_prefix)
    if slug.startswith("/"):
        slug = slug[1:]

    if strip_prefix and slug.startswith(strip_prefix):
        slug = slug[len(strip_prefix) + 1 :]

    logging.debug("<< " + strip_prefix + "   ./" + slug)
    return "./" + slug


def create_geometry_file(output_dir, row, field):
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
