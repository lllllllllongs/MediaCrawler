from unittest.mock import AsyncMock, MagicMock

import pytest

from media_platform.bilibili.login import BilibiliLogin


@pytest.mark.asyncio
async def test_qrcode_login_force_clicks_button(monkeypatch):
    login_button = AsyncMock()
    page = MagicMock()
    page.locator.return_value = login_button

    monkeypatch.setattr(
        "media_platform.bilibili.login.utils.find_login_qrcode",
        AsyncMock(return_value=None),
    )
    monkeypatch.setattr(
        "media_platform.bilibili.login.sys.exit",
        MagicMock(side_effect=SystemExit),
    )

    login = BilibiliLogin(
        login_type="qrcode",
        browser_context=MagicMock(),
        context_page=page,
    )
    with pytest.raises(SystemExit):
        await login.login_by_qrcode()

    login_button.click.assert_awaited_once_with(force=True)
