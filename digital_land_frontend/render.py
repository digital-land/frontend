import csv
import json
import logging
import re
from collections import OrderedDict, defaultdict
from pathlib import Path

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
        schema,
        dataset_path,
        url_root=None,
        key_fields=["organisation", "site"],
        group_type="organisation",
        group_field="organisation",
        group_list_field="organisations",
        docs="docs",
    ):
        self.name = name
        self.schema = schema
        self.dataset_path = dataset_path
        self.docs = Path(docs)
        self.key_fields = key_fields
        self.group_type = group_type
        self.group_field = group_field
        self.group_list_field = group_list_field
        self.env = setup_jinja()
        self.index = defaultdict(lambda: {"count": 0, "references": set(), "items": []})
        self.index_template = self.env.get_template("index.html")
        self.row_template = self.env.get_template("row.html")
        self.group_map = {}
        self.group_slug_seen = set()
        self.slug_seen = set()

        if url_root:
            self.env.globals["urlRoot"] = url_root
        else:
            self.env.globals["urlRoot"] = f"/{name.replace(' ', '-')}/"

    def add_to_group_index(self, row):
        if self.group_type and self.group_field in row and row[self.group_field]:
            groups = [row[self.group_field]]
        elif (
            self.group_type
            and self.group_list_field in row
            and row[self.group_list_field]
        ):
            groups = row[self.group_list_field].split(";")
        else:
            groups = ["no-group"]

        for group in groups:
            self.add_row_to_group_map(group, row)

    @property
    def group_index(self):
        for org, idx in self.group_map.items():
            self.group_map[org]["items"] = sorted(
                idx["items"], key=lambda x: AlphaNumericSort.alphanum(x["slug"])
            )

        result = OrderedDict(
            sorted(self.group_map.items(), key=lambda x: x[1]["name"] or "")
        )

        if "no-group" in result:
            result.move_to_end("no-group")

        return result

    def add_row_to_group_map(self, group, row):
        self.slug_seen.add(row["slug"])
        dupe_check_key = (group, row["slug"])
        if dupe_check_key in self.group_slug_seen:
            return

        if self.group_type is None:
            def name_map_func(name):
                return name
        elif self.group_type == "organisation":
            name_map_func = self.organisation_mapper.get_by_key
        else:
            raise NotImplementedError("group_type %s not supported" % self.group_type)

        o = {
            "name": name_map_func(group),
            "items": [],
        }
        self.group_map.setdefault(group, o)
        self.group_map[group]["items"].append(row)
        self.group_slug_seen.add(dupe_check_key)

    def render_pages(self):
        self.slugs = set()
        rows = []
        for idx, row in enumerate(csv.DictReader(open(self.dataset_path)), start=1):
            if not row["slug"]:
                continue  # skip rows without a unique slug

            self.add_to_group_index(row)

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
                schema=self.schema,
                breadcrumb=breadcrumb,
            )
            rows.append(row)
            self.add_to_index(row["slug"], row)
            self.slugs.add(row["slug"])

        self.index[""] = {
            "count": len(self.slug_seen),
            "groups": self.group_index,
            "group_type": self.group_type,
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
        self.index[stem].setdefault(
            "groups", {"no-group": {"items": [], "references": set()}}
        )
        self.index[stem].setdefault("count", 0)
        self.index[stem].setdefault("group_type", None)

        if name in self.index[stem]["groups"]["no-group"]["references"]:
            return

        self.index[stem]["groups"]["no-group"]["references"].add(name)
        self.index[stem]["count"] += 1
        index_entry = {
            "reference": format_name(name) if not row else name,
            "href": slug_to_relative_path(slug, strip_prefix=stem),
        }
        if row:
            index_entry["text"] = row["name"]
        self.index[stem]["groups"]["no-group"]["items"].append(index_entry)
        self._add_to_index(stem)

    def render_index_pages(self):
        for path, i in self.index.items():
            if path:
                slug = f"/{self.name}/{path}"
                download_url = None
            else:
                slug = f"/{self.name}"
                download_url = f"https://raw.githubusercontent.com/digital-land/permitted-development-right/main/{self.dataset_path}"
            if "items" in i:
                i["items"] = sorted(
                    i["items"], key=lambda x: AlphaNumericSort.alphanum(x["reference"])
                )
            logging.debug("rendering %s", path)
            self.render(
                self.docs / path / "index.html",
                self.index_template,
                index=i,
                data_type=self.name,
                schema=self.schema,
                breadcrumb=slug_to_breadcrumb(slug),
                download_url=download_url,
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

    logging.debug("<< " + str(strip_prefix) + "   ./" + slug)
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


class AlphaNumericSort:
    @staticmethod
    def convert(text):
        return int(text) if text.isdigit() else text

    @classmethod
    def alphanum(cls, key):
        return [cls.convert(c) for c in re.split("([0-9]+)", key)]
