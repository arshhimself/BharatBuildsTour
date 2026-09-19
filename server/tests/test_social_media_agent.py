"""Tests for Social Media Agent and Instagram publishing service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.config import get_settings
from app.modules.runs.manager_tools import InstagramPostInput, build_tools
from app.modules.social.service import format_caption, publish_instagram_post_async


def test_format_caption():
    assert format_caption("New stock arrived!", ["fashion", "#summer", "fashion", "#sale"]) == (
        "New stock arrived!\n\n#fashion #summer #sale"
    )
    assert format_caption("Check this out", None) == "Check this out"
    assert format_caption("", ["#tag1", "tag2"]) == "#tag1 #tag2"


@pytest.mark.anyio
async def test_publish_instagram_post_missing_credentials(monkeypatch):
    monkeypatch.setattr(
        get_settings(), "instagram_access_token", MagicMock(get_secret_value=lambda: "")
    )
    monkeypatch.setattr(get_settings(), "instagram_user_id", "")

    result = await publish_instagram_post_async("https://example.com/image.jpg", "Test Caption")
    assert result["success"] is False
    assert result["error_code"] == "CREDENTIALS_MISSING"


@pytest.mark.anyio
async def test_publish_instagram_post_invalid_image_url(monkeypatch):
    monkeypatch.setattr(
        get_settings(), "instagram_access_token", MagicMock(get_secret_value=lambda: "token123")
    )
    monkeypatch.setattr(get_settings(), "instagram_user_id", "17841400000000000")

    result = await publish_instagram_post_async("invalid-url", "Test Caption")
    assert result["success"] is False
    assert result["error_code"] == "INVALID_IMAGE_URL"


@pytest.mark.anyio
async def test_publish_instagram_post_success(monkeypatch):
    monkeypatch.setattr(
        get_settings(), "instagram_access_token", MagicMock(get_secret_value=lambda: "token123")
    )
    monkeypatch.setattr(get_settings(), "instagram_user_id", "17841400000000000")
    monkeypatch.setattr(get_settings(), "instagram_api_version", "v21.0")
    monkeypatch.setattr(get_settings(), "instagram_graph_url", "https://graph.facebook.com")

    mock_post = AsyncMock()

    # Container creation response
    res1 = MagicMock()
    res1.status_code = 200
    res1.json.return_value = {"id": "creation_container_999"}

    # Publish response
    res2 = MagicMock()
    res2.status_code = 200
    res2.json.return_value = {"id": "ig_media_123456"}

    res_status = MagicMock()
    res_status.status_code = 200
    res_status.json.return_value = {"status_code": "FINISHED", "status": "FINISHED"}

    mock_post.side_effect = [res1, res2]

    with (
        patch("httpx.AsyncClient.post", mock_post),
        patch("httpx.AsyncClient.get", AsyncMock(return_value=res_status)),
    ):
        result = await publish_instagram_post_async(
            image_url="https://example.com/item.jpg",
            caption="Awesome Product",
            hashtags=["#awesome", "products"],
        )

        assert result["success"] is True
        assert result["media_id"] == "ig_media_123456"
        assert result["platform"] == "instagram"


@pytest.mark.anyio
async def test_publish_instagram_post_container_failure(monkeypatch):
    monkeypatch.setattr(
        get_settings(), "instagram_access_token", MagicMock(get_secret_value=lambda: "token123")
    )
    monkeypatch.setattr(get_settings(), "instagram_user_id", "17841400000000000")

    res1 = MagicMock()
    res1.status_code = 400
    res1.json.return_value = {"error": {"message": "Invalid image format"}}

    with patch("httpx.AsyncClient.post", AsyncMock(return_value=res1)):
        result = await publish_instagram_post_async(
            image_url="https://example.com/bad.png",
            caption="Test",
        )
        assert result["success"] is False
        assert result["error_code"] == "CONTAINER_CREATION_FAILED"
        assert "Invalid image format" in result["message"]


def test_manager_tools_includes_instagram_post():
    tools = build_tools(db=None)
    tool_names = [t.name for t in tools]
    assert "publish_instagram_post" in tool_names

    ig_tool = next(t for t in tools if t.name == "publish_instagram_post")
    assert ig_tool.args_schema == InstagramPostInput
