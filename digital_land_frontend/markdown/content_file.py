#!/usr/bin/env python3

from frontmatter import Frontmatter
from digital_land_frontend.markdown.filter import compile_markdown


def create_breadcrumbs(output_path):
    parts = output_path.split("/")[1:-1]
    breadcrumbs = [{"text": "Digital Land", "href": "/"}]
    for idx, part in enumerate(parts):
        if (idx + 1) < len(parts):
            breadcrumbs.append(
                {
                    "text": part.capitalize().replace("-", " "),
                    "href": "/".join(parts[: idx + 1]),
                }
            )
        else:
            breadcrumbs.append({"text": part.capitalize().replace("-", " ")})
    return breadcrumbs


def read_content_file(filename, expanded=False, **kwargs):
    content = {}
    file_content = Frontmatter.read_file(filename)

    content["content"] = compile_markdown(file_content["body"])
    content["frontmatter"] = file_content["attributes"]
    content["title"] = (
        file_content["attributes"].get("title")
        if file_content["attributes"].get("title") is not None
        else filename.with_suffix("")
    )

    if file_content["attributes"].get("section") is not None:
        content["section"] = file_content["attributes"].get("section")

    if expanded:
        content["body"] = file_content["body"]

    return {**content, **kwargs}
