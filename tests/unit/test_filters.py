from digital_land_frontend.filters import (
    policy_mapper_filter,
    is_list,
    plan_type_mapper_filter,
    dev_doc_mapper_filter,
)


def test_policy_mapper_filter():
    s = "worminghallndp-NH1"

    assert policy_mapper_filter(s) == "New Houses"
    assert (
        policy_mapper_filter(s, "slug")
        == "/development-policy/local-authority-eng/BUC/worminghallndp-NH1"
    )
    assert (
        policy_mapper_filter(s, "url")
        == "https://digital-land.github.io/development-policy/local-authority-eng/BUC/worminghallndp-NH1"
    )


def test_is_list_filter():
    s = "not a list"
    ss = [
        "./3090/geometry.geojson",
        "./3091/geometry.geojson",
        "./3092/geometry.geojson",
    ]

    assert not is_list(s)
    assert is_list(ss)


def test_plan_type_filter():
    s = "local-plan"

    assert plan_type_mapper_filter(s) == "Local Plan"
    assert (
        plan_type_mapper_filter(s, "url")
        == "https://digital-land.github.io/development-plan-type/local-plan"
    )


def test_dev_doc_mapper_filter():
    doc_id = "neigh-plan-buc-astonclintonndp"

    assert dev_doc_mapper_filter(doc_id) == "Aston Clinton Neighbourhood Plan 2013-2033"
    assert (
        dev_doc_mapper_filter(doc_id, "url")
        == "https://digital-land.github.io/development-plan-document/local-authority-eng/BUC/neigh-plan-buc-astonclintonndp"
    )
