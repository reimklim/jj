import pytest
from aiohttp import FormData

import jj
from jj.middlewares import SelfMiddleware
from jj.mock import Mock, RemoteMock

from .._test_utils import run


@pytest.mark.asyncio
async def test_mock_form_data_match_urlencoded():
    mock = Mock()
    self_middleware = SelfMiddleware(mock.resolver)
    matcher, response = jj.match(form_data={"key": "value"}), jj.Response(status=200)

    async with run(mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)
        async with handler:
            resp = await client.post("/", data={"key": "value"})
            assert resp.status == 200


@pytest.mark.asyncio
async def test_mock_form_data_match_multipart():
    mock = Mock()
    self_middleware = SelfMiddleware(mock.resolver)
    matcher, response = jj.match(form_data={"key": "value"}), jj.Response(status=200)

    async with run(mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)
        async with handler:
            form = FormData()
            form.add_field("key", "value")
            resp = await client.post("/", data=form)
            assert resp.status == 200


@pytest.mark.asyncio
async def test_mock_form_data_match_wrong_content_type():
    mock = Mock()
    self_middleware = SelfMiddleware(mock.resolver)
    matcher, response = jj.match(form_data={"key": "value"}), jj.Response(status=200)

    async with run(mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)
        async with handler:
            resp = await client.post("/", data=b"key=value",
                                     headers={"Content-Type": "text/plain"})
            assert resp.status == 404


@pytest.mark.asyncio
async def test_mock_form_data_match_json_body():
    mock = Mock()
    self_middleware = SelfMiddleware(mock.resolver)
    matcher, response = jj.match(form_data={"key": "value"}), jj.Response(status=200)

    async with run(mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)
        async with handler:
            resp = await client.post("/", json={"key": "value"})
            assert resp.status == 404


@pytest.mark.asyncio
async def test_mock_form_data_match_wrong_value():
    mock = Mock()
    self_middleware = SelfMiddleware(mock.resolver)
    matcher, response = jj.match(form_data={"key": "value"}), jj.Response(status=200)

    async with run(mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)
        async with handler:
            resp = await client.post("/", data={"key": "another"})
            assert resp.status == 404


@pytest.mark.asyncio
async def test_mock_form_data_shorthand_matcher():
    mock = Mock()
    self_middleware = SelfMiddleware(mock.resolver)
    matcher, response = jj.match_form_data("key", "value"), jj.Response(status=200)

    async with run(mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)
        async with handler:
            resp = await client.post("/", data={"key": "value"})
            assert resp.status == 200
