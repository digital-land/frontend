import pytest

from digital_land_frontend.render import (
    slug_to_breadcrumb,
    slug_to_relative_path,
)


@pytest.mark.skip()
def test_add_to_index():
    # renderer = Renderer("some-name", "some-dataset")
    # renderer.add_to_index()
    raise Exception("Implement me")


def test_slug_to_relative_path():
    slug = "local-authority-eng/BUC/avdlp-GP2"

    path = slug_to_relative_path(slug)

    assert path == "./local-authority-eng/BUC/avdlp-GP2"


def test_slug_to_relative_path_strip_prefix():
    slug = "/development-policy/local-authority-eng/BUC/avdlp-GP2"

    path = slug_to_relative_path(slug, strip_prefix="development-policy/local-authority-eng")

    assert path == "./BUC/avdlp-GP2"


def test_slug_to_breadcrumb():
    slug = "/development-policy/local-authority-eng/BUC/avdlp-GP2"

    breadcrumb = slug_to_breadcrumb(slug)

    assert len(breadcrumb) == 4
    assert breadcrumb == [
        {"text": "Development Policy", "href": "../../../"},
        {"text": "Local Authority Eng", "href": "../../"},
        {"text": "BUC", "href": "../"},
        {"text": "avdlp-GP2"},
    ]
