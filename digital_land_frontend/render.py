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
    GeneralOrganisationMapper,
)

# TODO:
#   - add group_field to specification
#   - remove `references` from render parameters - use "seen" sets
#   - clean up template logic now that we always provide href, text and reference


class JinjaRenderer:
    def __init__(self, url_root, docs="docs"):
        self.docs = docs
        self.env = setup_jinja()
        self.env.globals["urlRoot"] = url_root
        self.env.trim_blocks = True
        self.env.lstrip_blocks = True
        self.template = {
            "index": self.env.get_template("index.html"),
            "row": self.env.get_template("row.html"),
        }

    def render_index(self, path, *args, **kwargs):
        JinjaRenderer._render(
            path,
            self.template["index"],
            **kwargs,
        )

    def render_row(self, path, **kwargs):
        JinjaRenderer._render(
            path,
            self.template["row"],
            **kwargs,
        )

    @staticmethod
    def _render(path, template, **kwargs):
        with open(path, "w") as f:
            logging.debug(f"creating {path}")
            f.write(template.render(**kwargs))


class Renderer:
    organisation_mapper = GeneralOrganisationMapper()
    geography_mapper = GeographyMapper()
    translations = str.maketrans({"/": "-", " ": "", "(": "", ")": "", "'": ""})
    geometry_fields = ["geometry", "point"]

    def __init__(
        self,
        name,
        url_root=None,
        key_fields=["organisation", "site"],
        group_field="organisation",
        group_list_field="organisations",
        docs="docs",
        renderer=None,
    ):
        self.name = name
        self.docs = Path(docs)
        self.key_fields = key_fields
        self.group_field = group_field
        self.group_list_field = group_list_field
        self.index = defaultdict(lambda: {"count": 0, "references": set(), "items": []})
        self.group_map = {}
        self.group_slug_seen = set()
        self.slug_seen = set()

        if not url_root:
            url_root = f"/{name.replace(' ', '-')}/"

        self.renderer = renderer or JinjaRenderer(url_root, docs)

    def add_to_group_index(self, row):
        if self.group_field and self.group_field in row and row[self.group_field]:
            groups = [row[self.group_field]]
        elif (
            self.group_field
            and self.group_list_field in row
            and row[self.group_list_field]
        ):
            groups = row[self.group_list_field].split(";")
        else:
            groups = [None]

        for group in groups:
            self.add_row_to_group_map(group, row)

    @property
    def group_index(self):
        for group, idx in self.group_map.items():
            self.group_map[group]["items"] = sorted(
                idx["items"], key=lambda x: AlphaNumericSort.alphanum(x["reference"])
            )

        result = OrderedDict(
            sorted(self.group_map.items(), key=lambda x: x[1]["text"] or "")
        )

        if self.group_field:
            return result
        else:
            return result[None]["items"]

    def add_row_to_group_map(self, group, row):
        self.slug_seen.add(row["slug"])
        dupe_check_key = (group, row["slug"])
        if dupe_check_key in self.group_slug_seen:
            return

        if self.group_field is None:

            def name_map_func(name):
                return name

        elif self.group_field == "organisation":
            name_map_func = self.organisation_mapper.get_name
        else:
            raise NotImplementedError("group_field %s not supported" % self.group_field)

        o = {
            "text": name_map_func(group) or group,
            "items": [],
        }
        self.group_map.setdefault(group, o)
        reference = row["slug"].split("/")[-1]
        self.group_map[group]["items"].append(
            self.index_entry(reference, row["name"], slug=row["slug"])
        )
        self.group_slug_seen.add(dupe_check_key)

    def render_dataset(self, dataset_path):
        self.render(csv.DictReader(open(dataset_path)))

    def render(self, reader):
        self.slugs = set()
        rows = []
        for idx, row in enumerate(reader, start=1):
            if not row["slug"]:
                continue  # skip rows without a unique slug

            self.add_to_group_index(row)

            if row["slug"] in self.slugs:
                logging.warning("Duplicate slug found: %s", row["slug"])

            breadcrumb = slug_to_breadcrumb(row["slug"])

            path = "/".join(row["slug"].split("/")[2:])  # strip the prefix from slug

            output_dir = self.docs / path
            if not output_dir.exists():
                output_dir.mkdir(parents=True)

            for field in self.geometry_fields:
                if field in row and row[field]:
                    create_geometry_file(output_dir, row, field)
                    row["geometry_url"] = "geometry.geojson"
                    break

            self.renderer.render_row(
                str(output_dir / "index.html"),
                row=row,
                data_type=self.name,
                breadcrumb=breadcrumb,
            )
            rows.append(row)
            self.add_to_index(row["slug"], row)
            self.slugs.add(row["slug"])

        root_index = {"data_type": self.name}
        if self.group_field:
            root_index["groups"] = self.group_index
        else:
            root_index["items"] = self.group_index

        root_index["group_field"] = self.group_field
        root_index["count"] = len(self.slug_seen)

        self.index[""] = root_index
        self.render_index_pages()

    def add_to_index(self, slug, row):
        _, __, stem = slug.split("/", 2)
        self._add_to_index(stem, row)

    def _add_to_index(self, slug, row=None):
        if slug.find("/") <= 0:
            # no more parts of the path to index
            return

        stem, name = slug.rsplit("/", 1)
        self.index[stem].setdefault("items", [])
        self.index[stem].setdefault("references", set())
        self.index[stem].setdefault("count", 0)
        self.index[stem].setdefault("group_field", None)

        if name in self.index[stem]["references"]:
            return

        self.index[stem]["references"].add(name)
        self.index[stem]["count"] += 1

        reference = format_name(name) if not row else name
        href = slug_to_relative_href(slug, strip_prefix=stem)
        text = row["name"] if row else None

        self.index[stem]["items"].append(self.index_entry(reference, text, href))
        self._add_to_index(stem)

    def index_entry(self, reference, text, href=None, slug=None):
        if href:
            return {"reference": reference, "text": text, "href": href}
        elif slug:
            return {"reference": reference, "text": text, "slug": slug}
        else:
            raise ValueError("index entry requires href or slug")

    def render_index_pages(self):
        for path, i in self.index.items():
            if path:
                slug = f"/{self.name}/{path}"
                download_url = None
            else:
                slug = f"/{self.name}"
                download_url = f"https://raw.githubusercontent.com/digital-land/{self.name}/main/dataset/{self.name}.csv"
            if "items" in i:
                for item in i["items"]:
                    if "slug" in item:
                        item["href"] = slug_to_relative_href(
                            item["slug"], "/".join([self.name, path])
                        )
                        del item["slug"]
                i["items"] = sorted(
                    i["items"], key=lambda x: AlphaNumericSort.alphanum(x["reference"])
                )

            for group in i.get("groups", {}).values():
                for item in group.get("items", []):
                    if "slug" in item:
                        item["href"] = slug_to_relative_href(
                            item["slug"], "/".join([self.name, path])
                        )
                        del item["slug"]

            logging.debug("rendering %s", path)
            self.renderer.render_index(
                str(self.docs / path / "index.html"),
                **i,
                breadcrumb=slug_to_breadcrumb(slug),
                download_url=download_url,
            )


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


def slug_to_relative_href(slug, strip_prefix=None):
    logging.debug(">> slug_to_relative_href(%s, %s)", slug, strip_prefix)
    if slug.startswith("/"):
        slug = slug[1:]

    if strip_prefix and slug.startswith(strip_prefix):
        slug = slug[len(strip_prefix) :]
        if slug.startswith("/"):
            slug = slug[1:]

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
