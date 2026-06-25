from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from media_platform.kuaishou.client import KuaiShouClient


def make_client():
    return KuaiShouClient(
        headers={},
        playwright_page=MagicMock(),
        cookie_dict={},
    )


@pytest.mark.asyncio
async def test_request_ignores_environment_proxy():
    response = MagicMock(spec=httpx.Response)
    http_client = AsyncMock()
    http_client.request.return_value = response
    context = AsyncMock()
    context.__aenter__.return_value = http_client

    with patch(
        "media_platform.kuaishou.client.make_async_client",
        return_value=context,
    ) as make_client_mock:
        result = await make_client()._request_with_retry("GET", "https://example.com")

    assert result is response
    make_client_mock.assert_called_once_with(proxy=None, trust_env=False)


@pytest.mark.asyncio
async def test_request_retries_transport_errors():
    response = MagicMock(spec=httpx.Response)
    http_client = AsyncMock()
    http_client.request.side_effect = [
        httpx.ConnectError("temporary failure"),
        response,
    ]
    context = AsyncMock()
    context.__aenter__.return_value = http_client

    with (
        patch(
            "media_platform.kuaishou.client.make_async_client",
            return_value=context,
        ),
        patch("media_platform.kuaishou.client.asyncio.sleep", new_callable=AsyncMock) as sleep,
    ):
        result = await make_client()._request_with_retry("GET", "https://example.com")

    assert result is response
    assert http_client.request.await_count == 2
    sleep.assert_awaited_once_with(2)
