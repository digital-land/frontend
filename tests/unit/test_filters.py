from digital_land_frontend.filters import (
    policy_mapper,
    is_list,
    plan_type_mapper,
    dev_doc_mapper,
    policy_category_mapper,
)


def test_policy_mapper_filter():
    s = "worminghallndp-NH1"

    assert policy_mapper.filter(s) == "New Houses"
    assert (
        policy_mapper.filter(s, "slug")
        == "/development-policy/local-authority-eng/BUC/worminghallndp-NH1"
    )
    assert (
        policy_mapper.filter(s, "url")
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

    assert plan_type_mapper.filter(s) == "Local Plan"
    assert (
        plan_type_mapper.filter(s, "url")
        == "https://digital-land.github.io/development-plan-type/local-plan"
    )


def test_dev_doc_mapper_filter():
    doc_id = "neigh-plan-buc-buckinghamndp"

    assert dev_doc_mapper.filter(doc_id) == "Buckingham Neighbourhood Plan"
    assert (
        dev_doc_mapper.filter(doc_id, "url")
        == "https://digital-land.github.io/development-plan-document/neighbourhood-plan-area/buckingham/neigh-plan-buc-buckinghamndp"
    )


def test_policy_category_mapper_filter():
    cat_id = "strategic-policy"

    assert policy_category_mapper.filter(cat_id) == "Strategic policy"
    assert (
        policy_category_mapper.filter(cat_id, "url")
        == "https://digital-land.github.io/development-policy-category/strategic-policy"
    )
