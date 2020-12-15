from digital_land_frontend.render import Renderer


def test_generate_slug():
    row = {"organisation": "local-authority-eng:YOR", "site": "SITE01"}

    slug = Renderer._generate_slug(row, "conservation-area", ["organisation", "site"])

    assert slug == "conservation-area/local-authority-eng/YOR/SITE01"


def test_generate_slug_strips_slashes():
    row = {"organisation": "local-authority-eng:YOR", "site": "SITE/01"}

    slug = Renderer._generate_slug(row, "conservation-area", ["organisation", "site"])

    assert slug == "conservation-area/local-authority-eng/YOR/SITE-01"
