from collections import OrderedDict

import pytest

from digital_land_frontend.render import (
    Renderer,
    slug_to_breadcrumb,
    slug_to_relative_href,
)


class SpyRenderer:
    def __init__(self):
        self.index_pages_rendered = {}
        self.row_pages_rendered = {}

    def render_row(self, path, **kwargs):
        self.row_pages_rendered[path] = kwargs

    def render_index(self, path, **kwargs):
        self.index_pages_rendered[path] = kwargs


@pytest.fixture()
def _dataset_reader():
    # deliberately out of order to test renderer sorting logic
    data = [
        {
            "dataset-name": "REF01",
            "name": "item-one",
            "slug": "/dataset-name/REF01",
            "organisation": "org-one",
            "blah": 1,
        },
        {
            "dataset-name": "REF03",
            "name": "item-three",
            "slug": "/dataset-name/REF03",
            "organisation": "org-one",
            "blah": 1,
        },
        {
            "dataset-name": "REF02",
            "name": "item-two",
            "slug": "/dataset-name/REF02",
            "organisation": "org-two",
            "blah": 1,
        },
        {
            "dataset-name": "REF/04",
            "name": "item-four",
            "slug": "/dataset-name/REF-04",
            "organisation": "org-one",
            "blah": 1,
        },
    ]
    return data


@pytest.fixture()
def dataset_simple_slug_reader(_dataset_reader):
    return [
        dict(row, slug=f"/dataset-name/{row['dataset-name'].replace('/', '-')}")
        for row in _dataset_reader
    ]


@pytest.fixture()
def dataset_multi_slug_reader(_dataset_reader):
    return [
        dict(
            row,
            slug=f"/dataset-name/{row['organisation']}/{row['dataset-name'].replace('/', '-')}",
        )
        for row in _dataset_reader
    ]


def test_render_with_index_grouping_and_sub_indexes(dataset_multi_slug_reader):
    spy_renderer = SpyRenderer()
    renderer = Renderer(
        "dataset-name",
        "dataset-name",
        group_field="organisation",
        renderer=spy_renderer,
    )
    renderer.render(dataset_multi_slug_reader)

    assert len(spy_renderer.row_pages_rendered) == 4
    for row in dataset_multi_slug_reader:
        assert spy_renderer.row_pages_rendered[
            f"docs/{row['organisation']}/{row['dataset-name'].replace('/', '-')}/index.html"
        ] == {
            "breadcrumb": [
                {"href": "../../", "text": "Dataset Name"},
                {"href": "../", "text": row["organisation"].replace("-", " ").title()},
                {"text": row["dataset-name"]},
            ],
            "data_type": "dataset-name",
            "row": row,
        }

    assert len(spy_renderer.index_pages_rendered) == 3
    assert set(spy_renderer.index_pages_rendered.keys()) == set(
        [
            "docs/index.html",
            "docs/org-one/index.html",
            "docs/org-two/index.html",
        ]
    )

    assert spy_renderer.index_pages_rendered["docs/index.html"] == {
        "data_type": "dataset-name",
        "breadcrumb": [{"text": "dataset-name"}],
        "count": 4,
        "download_url": "https://raw.githubusercontent.com/digital-land/dataset-name/main/dataset/dataset-name.csv",
        "group_field": "organisation",
        "groups": OrderedDict(
            {
                "org-one": {
                    "text": "org-one",
                    "items": [
                        {
                            "reference": "REF01",
                            "text": "item-one",
                            "href": "./org-one/REF01",
                        },
                        {
                            "reference": "REF03",
                            "text": "item-three",
                            "href": "./org-one/REF03",
                        },
                        {
                            "reference": "REF/04",
                            "text": "item-four",
                            "href": "./org-one/REF-04",
                        },
                    ],
                },
                "org-two": {
                    "text": "org-two",
                    "items": [
                        {
                            "reference": "REF02",
                            "text": "item-two",
                            "href": "./org-two/REF02",
                        }
                    ],
                },
            }
        ),
    }

    assert spy_renderer.index_pages_rendered["docs/org-one/index.html"] == {
        "breadcrumb": [{"href": "../", "text": "Dataset Name"}, {"text": "org-one"}],
        "count": 3,
        "download_url": None,
        "group_field": None,
        "items": [
            {"href": "./REF01", "reference": "REF01", "text": "item-one"},
            {"href": "./REF03", "reference": "REF03", "text": "item-three"},
            {"href": "./REF-04", "reference": "REF/04", "text": "item-four"},
        ],
        "references": {"REF01", "REF03", "REF/04"},
    }

    assert spy_renderer.index_pages_rendered["docs/org-two/index.html"] == {
        "breadcrumb": [{"href": "../", "text": "Dataset Name"}, {"text": "org-two"}],
        "count": 1,
        "download_url": None,
        "group_field": None,
        "items": [
            {"href": "./REF02", "reference": "REF02", "text": "item-two"},
        ],
        "references": {"REF02"},
    }


def test_render_with_index_grouping(dataset_simple_slug_reader):
    spy_renderer = SpyRenderer()
    renderer = Renderer(
        "dataset-name",
        "dataset-name",
        group_field="organisation",
        renderer=spy_renderer,
    )
    renderer.render(dataset_simple_slug_reader)

    assert len(spy_renderer.row_pages_rendered) == 4
    for row in dataset_simple_slug_reader:
        assert spy_renderer.row_pages_rendered[
            f"docs/{row['dataset-name'].replace('/', '-')}/index.html"
        ] == {
            "breadcrumb": [
                {"href": "../", "text": "Dataset Name"},
                {"text": row["dataset-name"]},
            ],
            "data_type": "dataset-name",
            "row": row,
        }

    assert len(spy_renderer.index_pages_rendered) == 1
    assert spy_renderer.index_pages_rendered["docs/index.html"] == {
        "data_type": "dataset-name",
        "breadcrumb": [{"text": "dataset-name"}],
        "download_url": "https://raw.githubusercontent.com/digital-land/dataset-name/main/dataset/dataset-name.csv",
        "count": 4,
        "group_field": "organisation",
        "groups": OrderedDict(
            {
                "org-one": {
                    "text": "org-one",
                    "items": [
                        {"reference": "REF01", "text": "item-one", "href": "./REF01"},
                        {"reference": "REF03", "text": "item-three", "href": "./REF03"},
                        {
                            "reference": "REF/04",
                            "text": "item-four",
                            "href": "./REF-04",
                        },
                    ],
                },
                "org-two": {
                    "text": "org-two",
                    "items": [
                        {"reference": "REF02", "text": "item-two", "href": "./REF02"}
                    ],
                },
            }
        ),
    }


def test_render_with_no_index_grouping(dataset_simple_slug_reader):
    spy_renderer = SpyRenderer()
    renderer = Renderer(
        "dataset-name", "dataset-name", group_field=None, renderer=spy_renderer
    )
    renderer.render(dataset_simple_slug_reader)

    assert len(spy_renderer.row_pages_rendered) == 4
    for row in dataset_simple_slug_reader:
        assert spy_renderer.row_pages_rendered[
            f"docs/{row['dataset-name'].replace('/', '-')}/index.html"
        ] == {
            "breadcrumb": [
                {"href": "../", "text": "Dataset Name"},
                {"text": row["dataset-name"]},
            ],
            "data_type": "dataset-name",
            "row": row,
        }

    assert len(spy_renderer.index_pages_rendered) == 1
    assert spy_renderer.index_pages_rendered["docs/index.html"] == {
        "data_type": "dataset-name",
        "breadcrumb": [{"text": "dataset-name"}],
        "download_url": "https://raw.githubusercontent.com/digital-land/dataset-name/main/dataset/dataset-name.csv",
        "count": 4,
        "group_field": None,
        "items": [
            {"reference": "REF01", "text": "item-one", "href": "./REF01"},
            {"reference": "REF02", "text": "item-two", "href": "./REF02"},
            {"reference": "REF03", "text": "item-three", "href": "./REF03"},
            {
                "reference": "REF/04",
                "text": "item-four",
                "href": "./REF-04",
            },
        ],
    }


def test_slug_to_relative_href():
    slug = "local-authority-eng/BUC/avdlp-GP2"

    path = slug_to_relative_href(slug)

    assert path == "./local-authority-eng/BUC/avdlp-GP2"


def test_slug_to_relative_href_strip_prefix():
    slug = "/development-policy/local-authority-eng/BUC/avdlp-GP2"

    path = slug_to_relative_href(
        slug, strip_prefix="development-policy/local-authority-eng"
    )

    assert path == "./BUC/avdlp-GP2"


def test_slug_to_breadcrumb():
    slug = "/development-policy/local-authority-eng/BUC/avdlp-GP2"
    reference = "avdlp-GP2"

    breadcrumb = slug_to_breadcrumb(slug, reference)

    assert len(breadcrumb) == 4
    assert breadcrumb == [
        {"text": "Development Policy", "href": "../../../"},
        {"text": "Local Authority Eng", "href": "../../"},
        {"text": "BUC", "href": "../"},
        {"text": "avdlp-GP2"},
    ]
