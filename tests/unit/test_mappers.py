import re

import pytest

from digital_land_frontend.jinja_filters.mappers import GeneralMapper, Mapper


class SpyMapper(Mapper):
    def __init__(self):
        super(SpyMapper, self).__init__()
        self.called_with = []

    def get_name(self, k):
        self.called_with.append(("get_name", k))
        return "something"

    def get_url(self, k):
        self.called_with.append(("get_url", k))
        return "something"


@pytest.fixture()
def mapper():
    class SpyMapperOne(SpyMapper):
        dataset_urls = []
        matcher = re.compile(r"mapper-one:")

    class SpyMapperTwo(SpyMapper):
        dataset_urls = []
        matcher = re.compile(r"mapper-two:")

    class TestGeneralMapper(GeneralMapper):
        spy_mapper_one = SpyMapperOne()
        spy_mapper_two = SpyMapperTwo()
        mappers = [spy_mapper_one, spy_mapper_two]

    return TestGeneralMapper()


def test_general_mapper(mapper):
    mapper.get_name("mapper-one:key-one")
    mapper.get_name("mapper-two:key-two")
    mapper.get_url("mapper-two:key-two")

    assert len(mapper.spy_mapper_one.called_with) == 1
    assert mapper.spy_mapper_one.called_with[0] == (
        "get_name",
        "mapper-one:key-one",
    )

    assert len(mapper.spy_mapper_two.called_with) == 2
    assert mapper.spy_mapper_two.called_with[0] == (
        "get_name",
        "mapper-two:key-two",
    )
    assert mapper.spy_mapper_two.called_with[1] == (
        "get_url",
        "mapper-two:key-two",
    )


def test_general_mapper_unmatched_key(mapper):
    with pytest.raises(ValueError, match=r"^no mapper found"):
        mapper.get_name("bad-mapper:key")
