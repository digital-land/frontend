import datetime

import pytest
from digital_land.specification import Specification

from digital_land_frontend.filters import (
    MapperFilter,
    contains_historical,
    is_historical,
    is_list,
    readable_date_filter,
    total_items_filter,
)
from digital_land_frontend.jinja_filters.category_mappers import (
    PlanTypeMapper,
    PolicyCategoryMapper,
)
from digital_land_frontend.jinja_filters.mappers import (
    DevelopmentDocMapper,
)

SPECIFICATION = Specification("specification")


# def test_policy_mapper_filter():
#     policy_mapper = MapperFilter(PolicyMapper())

#     s = "worminghallndp-NH1"

#     assert policy_mapper.filter(s) == "New Houses"
#     assert (
#         policy_mapper.filter(s, "slug")
#         == "/development-policy/local-authority-eng/BUC/worminghallndp-NH1"
#     )
#     assert (
#         policy_mapper.filter(s, "url")
#         == "https://digital-land.github.io/development-policy/local-authority-eng/BUC/worminghallndp-NH1"
#     )


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
    plan_type_mapper = MapperFilter(PlanTypeMapper())
    s = "local-plan"

    assert plan_type_mapper.filter(s) == "Local Plan"
    assert (
        plan_type_mapper.filter(s, "url")
        == "https://digital-land.github.io/development-plan-type/local-plan"
    )


def test_dev_doc_mapper_filter():
    dev_doc_mapper = MapperFilter(DevelopmentDocMapper())
    doc_id = "neigh-plan-buc-buckinghamndp"

    assert dev_doc_mapper.filter(doc_id) == "Buckingham Neighbourhood Plan"
    assert (
        dev_doc_mapper.filter(doc_id, "url")
        == "https://digital-land.github.io/development-plan-document/neighbourhood-plan-area/buckingham/neigh-plan-buc-buckinghamndp"
    )


def test_policy_category_mapper_filter():
    policy_category_mapper = MapperFilter(PolicyCategoryMapper())
    cat_id = "strategic-policy"

    assert policy_category_mapper.filter(cat_id) == "Strategic policy"
    assert (
        policy_category_mapper.filter(cat_id, "url")
        == "https://digital-land.github.io/development-policy-category/strategic-policy"
    )


# def test_mapper_router_filter():
#     category_mapper_router = MapperRouter(
#         {
#             "development-policy-category": MapperFilter(PolicyCategoryMapper()),
#             "development-plan-type": MapperFilter(PlanTypeMapper()),
#             "developer-agreement-type": MapperFilter(DeveloperAgreementTypeMapper()),
#         },
#         SPECIFICATION,
#     )

#     # test development plan type mapper
#     pt = "local-plan"
#     assert category_mapper_router.route(pt, "development-plan-type") == "Local Plan"
#     assert (
#         category_mapper_router.route(pt, "development-plan-type", "url")
#         == "https://digital-land.github.io/development-plan-type/local-plan"
#     )

#     # test development policy category mapper
#     c = "strategic-policy"
#     assert (
#         category_mapper_router.route(c, "development-policy-category")
#         == "Strategic policy"
#     )
#     assert (
#         category_mapper_router.route(c, "development-policy-category", "url")
#         == "https://digital-land.github.io/development-policy-category/strategic-policy"
#     )

# test developer agreement type mapper
# dat = "section-106"
# assert (
#     category_mapper_router.route(dat, "developer-agreement-type") == "Section 106"
# )

# assert (
#     category_mapper_router.route(dat, "developer-agreement-type", "slug")
#     == "/developer-agreement-type/section-106"
# )


# def test_mapper_router_unmatched_key():
#     category_mapper_router = MapperRouter(
#         {"development-policy-category": MapperFilter(PolicyCategoryMapper())},
#         SPECIFICATION,
#     )
#     with pytest.raises(ValueError, match=r"^no mapper found"):
#         category_mapper_router.route("local-plan", "bad-key")


def test_is_historical():
    with pytest.raises(ValueError, match=r"does not contain end-date"):
        is_historical({})

        {"development-policy-category": MapperFilter(PolicyCategoryMapper())},
        SPECIFICATION,
        is_historical("")

    assert is_historical({"name": "blah", "end-date": ""}) is False
    assert is_historical({"name": "blah", "end-date": "2036-02-01"}) is False
    assert is_historical({"name": "blah", "end-date": "2021-02-01"}) is True


@pytest.fixture()
def _item_data():
    data = [{"name": "blah1", "end-date": ""}, {"name": "blah2", "end-date": ""}]
    return data


def test_contains_historical(_item_data):
    assert contains_historical(_item_data) is False

    _item_data.append({"name": "blah3", "end-date": "2021-02-02"})
    assert contains_historical(_item_data) is True


def test_contains_historical_future_date(_item_data):
    _item_data.append({"name": "blah3", "end-date": "2036-02-02"})
    assert contains_historical(_item_data) is False


def test_contains_historical_not_a_list():
    with pytest.raises(ValueError, match=r"not a list"):
        contains_historical("bad value")


def test_total_items_filter():
    d = {"obj1": [1, 2, 3], "obj2": [4, 5, 6]}
    not_dict = []

    assert total_items_filter(d) == 6
    assert total_items_filter(not_dict) is None


def test_readable_date_filter():
    d = "2020-07-10"
    dt = datetime.datetime.strptime(d, "%Y-%m-%d")

    assert readable_date_filter(dt) == "10 July 2020"
