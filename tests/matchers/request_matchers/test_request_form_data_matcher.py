from unittest.mock import AsyncMock, Mock, call, sentinel

import pytest
from multidict import MultiDict

from jj.matchers import AttributeMatcher, FormDataMatcher, RequestMatcher
from jj.matchers.attribute_matchers import MultiDictMatcher

from ..._test_utils.fixtures import request_, resolver_
from ..._test_utils.steps import given, then, when

__all__ = ("request_", "resolver_",)


@pytest.mark.asyncio
@pytest.mark.parametrize(("expected", "actual", "res"), [
    ({}, {}, True),
    ([], {}, True),
    ({}, {"key": "1"}, True),
    ([], {"key": "1"}, True),

    ({"key": "1"}, {}, False),
    ({"key": "1"}, {"key": "1"}, True),
    ({"key1": "1"}, {"key1": "1", "key2": "2"}, True),
    ({"key1": "1", "key2": "2"}, {"key1": "1"}, False),
    ({"key1": "1", "key2": "2"}, {"key1": "1", "key2": "2"}, True),

    ([("key", "1"), ("key", "2")], [], False),
    ([("key", "1"), ("key", "2")], [("key", "1")], False),
    ([("key", "1"), ("key", "2")], [("key", "2")], False),
    ([("key", "1"), ("key", "2")], [("key", "1"), ("key", "2")], True),
    ([("key", "1"), ("key", "2")], [("key", "1"), ("key", "3")], False),

    ({"key": "1"}, [("key", "1")], True),
    ({"key": "1"}, [("key", "1"), ("key", "2")], True),
    ({"key": "1"}, [("key", "3"), ("key", "2")], False),

    ({"key": ""}, [("key", "")], True),
    ({"a": "b"}, {"a": "b"}, True),
    ({"a": "b"}, {"a": "B"}, False),
])
async def test_form_data_matcher(expected, actual, res, *, resolver_, request_):
    with given:
        request_.post = AsyncMock()
        request_.post_data = MultiDict(actual)
        matcher = FormDataMatcher(expected, resolver=resolver_)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is res


@pytest.mark.asyncio
@pytest.mark.parametrize(("ret_val", "form_data"), [
    (True, {}),
    (False, {"key": "val"}),
    (True, [("key", "1"), ("key", "2")]),
    (False, [("key1", "1"), ("key2", "2")]),
])
async def test_form_data_matcher_with_custom_submatcher(
    ret_val, form_data, *, resolver_, request_
):
    with given:
        request_.post = AsyncMock()
        request_.post_data = MultiDict(form_data)
        submatcher_ = Mock(AttributeMatcher, match=AsyncMock(return_value=ret_val))
        matcher = FormDataMatcher(submatcher_, resolver=resolver_)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is ret_val
        assert submatcher_.mock_calls == [call.match(request_.post_data)]


@pytest.mark.asyncio
async def test_form_data_matcher_when_body_read_fails(*, resolver_, request_):
    with given:
        request_.post = AsyncMock(side_effect=ValueError("broken body"))
        matcher = FormDataMatcher({"key": "value"}, resolver=resolver_)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is False


def test_is_instance_of_request_matcher(*, resolver_):
    with given:
        matcher = FormDataMatcher({}, resolver=resolver_)

    with when:
        actual = isinstance(matcher, RequestMatcher)

    with then:
        assert actual is True


@pytest.mark.parametrize(("form_data", "representation"), [
    ({}, "[]"),
    ({"KEY": "Val"}, "[('KEY', 'Val')]"),
    ({"key1": "1", "key2": "2"}, "[('key1', '1'), ('key2', '2')]"),
])
def test_repr(form_data, representation, *, resolver_):
    with given:
        resolver_.__repr__ = Mock(return_value="<Resolver>")
        matcher = FormDataMatcher(form_data, resolver=resolver_)

    with when:
        actual = repr(matcher)

    with then:
        expected = f"FormDataMatcher(MultiDictMatcher({representation}), resolver=<Resolver>)"
        assert actual == expected


def test_pack(*, resolver_):
    with given:
        submatcher = MultiDictMatcher([("key", "1"), ("key", "2")])
        matcher = FormDataMatcher(submatcher, resolver=resolver_)

    with when:
        actual = matcher.__packed__()

    with then:
        assert actual == {"form_data": submatcher}


def test_unpack(*, resolver_):
    with given:
        submatcher = MultiDictMatcher([("key", "1"), ("key", "2")])
        kwargs = {
            "form_data": submatcher,
            "resolver": resolver_,
            "future_field": sentinel,
        }

    with when:
        actual = FormDataMatcher.__unpacked__(**kwargs)

    with then:
        assert isinstance(actual, FormDataMatcher)


def test_sub_matcher_property(*, resolver_):
    with given:
        sub_matcher = MultiDictMatcher([("key", "1"), ("key", "2")])
        matcher = FormDataMatcher(sub_matcher, resolver=resolver_)

    with when:
        actual = matcher.sub_matcher

    with then:
        assert actual == sub_matcher
