import json
import logging
import re
from collections import OrderedDict, defaultdict
from pathlib import Path

import shapely.wkt
from digital_land.model.entity import Entity
from digital_land.repository.entry_repository import EntryRepository

from digital_land_frontend.jinja import setup_jinja
from digital_land_frontend.jinja_filters.mappers import (
    GeneralOrganisationMapper,
    GeographyMapper,
)

# TODO:
#   - add group_field to specification
#   - remove `references` from render parameters - use "seen" sets
#   - clean up template logic now that we always provide href, text and reference


def generate_download_link(pipeline_name):
    urls = {
        "contribution-funding-status": "https://raw.githubusercontent.com/digital-land/developer-contributions-collection/main/dataset/contribution-funding-status.csv",
        "contribution-purpose": "https://raw.githubusercontent.com/digital-land/developer-contributions-collection/main/dataset/contribution-purpose.csv",
        "developer-agreement": "https://raw.githubusercontent.com/digital-land/developer-contributions-collection/main/dataset/developer-agreement.csv",
        "developer-agreement-contribution": "https://raw.githubusercontent.com/digital-land/developer-contributions-collection/main/dataset/developer-agreement-contribution.csv",
        "developer-agreement-transaction": "https://raw.githubusercontent.com/digital-land/developer-contributions-collection/main/dataset/developer-agreement-transaction.csv",
        "developer-agreement-type": "https://raw.githubusercontent.com/digital-land/developer-contributions-collection/main/dataset/developer-agreement-type.csv",
    }
    if pipeline_name in urls:
        return urls[pipeline_name]
    return f"https://raw.githubusercontent.com/digital-land/{pipeline_name}-collection/main/dataset/{pipeline_name}.csv"


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
        pipeline_name,
        schema,
        typology,
        key_field,
        url_root=None,
        group_field="organisation",
        group_list_field="organisations",
        docs="docs",
        renderer=None,
        limit=None,
    ):
        self.pipeline_name = pipeline_name
        self.schema = schema
        self.typology = typology
        self.docs = Path(docs)
        self.key_field = key_field
        self.group_field = group_field
        self.group_list_field = group_list_field
        self.index = defaultdict(lambda: {"count": 0, "references": set(), "items": []})
        self.group_map = {}
        self.group_slug_seen = set()
        self.slug_seen = set()
        self.limit = limit

        if not url_root:
            url_root = f"/{pipeline_name.replace(' ', '-')}/"

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
        reference = (
            row[self.key_field] if self.key_field in row else row["slug"].split("/")[-1]
        )
        self.group_map[group]["items"].append(
            self.index_entry(
                reference,
                self.row_name(row),
                slug=row["slug"],
                end_date=row.get("end-date", None),
            )
        )
        self.group_slug_seen.add(dupe_check_key)

    def render_dataset(self, dataset_path):
        repo = EntryRepository(dataset_path)
        entities = repo.list_entities()
        reader = (
            Entity(repo.find_by_entity(entity), self.schema) for entity in entities
        )
        self.render(reader)

    def render(self, reader):
        self.slugs = set()
        rows = []
        for idx, entity in enumerate(reader, start=1):
            if self.limit and idx > self.limit:
                break

            row = entity.snapshot()

            if not row:
                continue  # Sometimes there are no active entries (all in the future)

            if not row["slug"]:
                continue  # skip rows without a unique slug

            self.add_to_group_index(row)

            if row["slug"] in self.slugs:
                logging.warning("Duplicate slug found: %s", row["slug"])

            breadcrumb = slug_to_breadcrumb(row["slug"], row[self.key_field])

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
                entity=entity,
                pipeline_name=self.pipeline_name,
                breadcrumb=breadcrumb,
                schema=self.schema,
                typology=self.typology,
                key_field=self.key_field,
            )
            rows.append(row)
            self.add_to_index(row["slug"], row)
            self.slugs.add(row["slug"])

        root_index = {"pipeline_name": self.pipeline_name}
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

        # safer to use tke key_field if available
        if row:
            name = row[self.key_field]

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
        text = self.row_name(row) if row else None
        end_date = row.get("end-date", "") if row else ""

        self.index[stem]["items"].append(
            self.index_entry(reference, text, href, end_date=end_date)
        )
        self._add_to_index(stem)

    def index_entry(self, reference, text, href=None, slug=None, end_date=""):
        if href:
            return {
                "reference": reference,
                "text": text,
                "href": href,
                "end-date": end_date,
            }
        elif slug:
            return {
                "reference": reference,
                "text": text,
                "slug": slug,
                "end-date": end_date,
            }
        else:
            raise ValueError("index entry requires href or slug")

    def render_index_pages(self):
        for path, i in self.index.items():
            if path:
                slug = f"/{self.pipeline_name}/{path}"
                download_url = None
            else:
                slug = f"/{self.pipeline_name}"
                download_url = generate_download_link(self.pipeline_name)
            if "items" in i:
                for item in i["items"]:
                    if "slug" in item:
                        item["href"] = slug_to_relative_href(
                            item["slug"], "/".join([self.pipeline_name, path])
                        )
                        del item["slug"]
                i["items"] = sorted(
                    i["items"], key=lambda x: AlphaNumericSort.alphanum(x["reference"])
                )

            for group in i.get("groups", {}).values():
                for item in group.get("items", []):
                    if "slug" in item:
                        item["href"] = slug_to_relative_href(
                            item["slug"], "/".join([self.pipeline_name, path])
                        )
                        del item["slug"]

            logging.debug("rendering %s", path)
            self.renderer.render_index(
                str(self.docs / path / "index.html"),
                **i,
                breadcrumb=slug_to_breadcrumb(slug),
                download_url=download_url,
            )

    def row_name(self, row):
        if self.pipeline_name == "developer-agreement":
            if row.get("developer-agreement-type") and row.get("planning-application"):
                return f"{row['developer-agreement-type'].title()} agreement for planning application {row['planning-application']}"
        if "name" in row:
            return row["name"]
        return row[self.key_field]


re_all_upper = re.compile(r"^[A-Z]*$")
re_strip = re.compile(r"[^a-zA-Z]")


def format_name(name):
    if re_all_upper.match(name):
        return name
    return re_strip.sub(" ", name).title()


def slug_to_breadcrumb(slug, reference=None):
    logging.debug(">> slug_to_breadcumb(%s)", slug)
    next_relative_path = "../"
    breadcrumb = []
    first_item = True
    for part in slug.split("/")[-1:0:-1]:
        if first_item:
            text = reference if reference else part
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
