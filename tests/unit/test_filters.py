from digital_land_frontend.filters import (
    policy_to_name_filter,
    policy_to_slug_filter,
    policy_url_filter,
    is_list,
    plan_type_mapper_filter,
)


def test_policy_to_name_filter():
    s = "bmwlp-P1"

    assert policy_to_name_filter(s) == "Safeguarding Mineral Resources"


def test_policy_to_url():
    s = "worminghallndp-NH1"

    assert (
        policy_to_slug_filter(s)
        == "/development-policy/local-authority-eng/BUC/worminghallndp-NH1"
    )


def test_policy_url_filter():
    s = "worminghallndp-NH1"

    assert (
        policy_url_filter(s)
        == "https://digital-land.github.io/development-policy/local-authority-eng/BUC/worminghallndp-NH1"
    )


def test_is_list_filter_not_a_list():
    s = "not a list"

    assert not is_list(s)


def test_is_list_filter_list():
    s = [
        "./3090/geometry.geojson",
        "./3091/geometry.geojson",
        "./3092/geometry.geojson",
    ]

    assert is_list(s)


def test_plan_type_filter():
    s = "local-plan"

    assert plan_type_mapper_filter(s) == "Local Plan"


def test_plan_type_filter_get_url():
    s = "local-plan"

    assert (
        plan_type_mapper_filter(s, "url")
        == "https://digital-land.github.io/development-plan-type/local-plan"
    )
