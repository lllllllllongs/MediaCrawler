from unittest.mock import AsyncMock, MagicMock

import pytest

from media_platform.kuaishou.login import KuaishouLogin


def make_login(page):
    return KuaishouLogin(
        login_type="qrcode",
        browser_context=MagicMock(),
        context_page=page,
    )


def prepare_exit(monkeypatch):
    monkeypatch.setattr(
        "media_platform.kuaishou.login.utils.find_login_qrcode",
        AsyncMock(return_value=None),
    )
    monkeypatch.setattr(
        "media_platform.kuaishou.login.sys.exit",
        MagicMock(side_effect=SystemExit),
    )


@pytest.mark.asyncio
async def test_qrcode_login_uses_already_open_modal(monkeypatch):
    login_button = AsyncMock()
    login_modal = AsyncMock()
    login_modal.count.return_value = 1
    page = MagicMock()
    page.locator.side_effect = [login_button, login_modal]
    prepare_exit(monkeypatch)

    with pytest.raises(SystemExit):
        await make_login(page).login_by_qrcode()

    login_button.click.assert_not_awaited()


@pytest.mark.asyncio
async def test_qrcode_login_force_clicks_when_modal_is_closed(monkeypatch):
    login_button = AsyncMock()
    login_modal = AsyncMock()
    login_modal.count.return_value = 0
    page = MagicMock()
    page.locator.side_effect = [login_button, login_modal]
    prepare_exit(monkeypatch)

    with pytest.raises(SystemExit):
        await make_login(page).login_by_qrcode()

    login_button.click.assert_awaited_once_with(force=True)
