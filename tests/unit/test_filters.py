import pytest

from digital_land_frontend.filters import (
    policy_mapper,
    is_list,
    plan_type_mapper,
    dev_doc_mapper,
    policy_category_mapper,
    category_mapper_router,
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


def test_mapper_router_filter():

    # test development plan type mapper
    pt = "local-plan"
    assert category_mapper_router.route(pt, "development-plan-type") == "Local Plan"
    assert (
        category_mapper_router.route(pt, "development-plan-type", "url")
        == "https://digital-land.github.io/development-plan-type/local-plan"
    )

    # test development policy category mapper
    c = "strategic-policy"
    assert (
        category_mapper_router.route(c, "development-policy-category")
        == "Strategic policy"
    )
    assert (
        category_mapper_router.route(c, "development-policy-category", "url")
        == "https://digital-land.github.io/development-policy-category/strategic-policy"
    )

    # test developer agreement type mapper
    dat = "section-106"
    assert (
        category_mapper_router.route(dat, "developer-agreement-type") == "Section 106"
    )

    assert (
        category_mapper_router.route(dat, "developer-agreement-type", "slug")
        == "/developer-agreement-type/section-106"
    )


def test_mapper_router_unmatched_key():
    with pytest.raises(ValueError, match=r"^no mapper found"):
        category_mapper_router.route("local-plan", "bad-key")
