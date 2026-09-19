from __future__ import annotations

"""Instagram publishing service for Social Media Agent."""

import logging
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.modules.social.models import SocialPost
from app.modules.social.schemas import InstagramPublishResponse

logger = logging.getLogger(__name__)


def format_caption(caption: str, hashtags: Optional[list[str]] = None) -> str:
    """Format caption with normalized hashtags, avoiding double '#' and duplicates."""
    clean_caption = (caption or "").strip()
    if not hashtags:
        return clean_caption

    normalized_tags: list[str] = []
    seen: set[str] = set()

    for tag in hashtags:
        tag_str = str(tag).strip()
        if not tag_str:
            continue
        # Remove leading '#' if present to normalize
        clean_tag = tag_str.lstrip("#").strip()
        if clean_tag and clean_tag.lower() not in seen:
            seen.add(clean_tag.lower())
            normalized_tags.append(f"#{clean_tag}")

    if not normalized_tags:
        return clean_caption

    tags_block = " ".join(normalized_tags)
    if clean_caption:
        return f"{clean_caption}\n\n{tags_block}"
    return tags_block


async def publish_instagram_post_async(
    image_url: str,
    caption: str,
    hashtags: Optional[list[str]] = None,
    db: Optional[Session] = None,
) -> dict[str, Any]:
    """Publish a public image post to Instagram via Instagram Graph API."""
    settings = get_settings()
    access_token = settings.instagram_access_token.get_secret_value()
    user_id = settings.instagram_user_id
    api_version = settings.instagram_api_version
    graph_url = settings.instagram_graph_url

    if not access_token or not user_id:
        msg = "Instagram API credentials (INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_USER_ID) not configured."
        logger.warning(msg)
        return InstagramPublishResponse(
            success=False,
            message=msg,
            error_code="CREDENTIALS_MISSING",
        ).model_dump()

    if not image_url or not (image_url.startswith("http://") or image_url.startswith("https://")):
        msg = "Invalid image URL. Must be a valid public HTTP or HTTPS URL."
        return InstagramPublishResponse(
            success=False,
            message=msg,
            error_code="INVALID_IMAGE_URL",
        ).model_dump()

    full_caption = format_caption(caption, hashtags)
    base_url = f"{graph_url.rstrip('/')}/{api_version}/{user_id}"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            # Stage 1: Create Media Container
            container_res = await client.post(
                f"{base_url}/media",
                headers=headers,
                data={"image_url": image_url, "caption": full_caption},
            )
            container_data = container_res.json()

            if container_res.status_code >= 400 or "id" not in container_data:
                err_msg = container_data.get("error", {}).get("message", "Media container creation failed.")
                logger.error("Instagram container creation failed: %s", err_msg)
                _record_post_status(db, image_url, full_caption, status="FAILED", error=err_msg)
                return InstagramPublishResponse(
                    success=False,
                    message=f"Failed to create Instagram media container: {err_msg}",
                    error_code="CONTAINER_CREATION_FAILED",
                ).model_dump()

            creation_id = container_data["id"]

            # Poll container status until ready
            import asyncio
            status_code = "IN_PROGRESS"
            for _ in range(10):
                status_res = await client.get(
                    f"{graph_url.rstrip('/')}/{api_version}/{creation_id}",
                    headers=headers,
                    params={"fields": "status_code,status"},
                )
                if status_res.status_code == 200:
                    status_code = status_res.json().get("status_code", "IN_PROGRESS")
                    if status_code in ("FINISHED", "ERROR", "EXPIRED"):
                        break
                await asyncio.sleep(2)

            if status_code != "FINISHED":
                err_msg = f"Container processing did not finish in time (status: {status_code})."
                logger.error(err_msg)
                _record_post_status(db, image_url, full_caption, status="FAILED", error=err_msg)
                return InstagramPublishResponse(
                    success=False,
                    message=f"Failed to publish Instagram media: {err_msg}",
                    error_code="CONTAINER_PROCESSING_FAILED",
                ).model_dump()

            # Stage 2: Publish Media Container
            publish_res = await client.post(
                f"{base_url}/media_publish",
                headers=headers,
                data={"creation_id": creation_id},
            )
            publish_data = publish_res.json()

            if publish_res.status_code >= 400 or "id" not in publish_data:
                err_msg = publish_data.get("error", {}).get("message", "Media publish failed.")
                logger.error("Instagram media publish failed: %s", err_msg)
                _record_post_status(db, image_url, full_caption, status="FAILED", error=err_msg)
                return InstagramPublishResponse(
                    success=False,
                    message=f"Failed to publish Instagram media: {err_msg}",
                    error_code="PUBLISH_FAILED",
                ).model_dump()

            media_id = publish_data["id"]
            _record_post_status(
                db,
                image_url,
                full_caption,
                status="PUBLISHED",
                media_id=media_id,
                account_id=user_id,
            )

            return InstagramPublishResponse(
                success=True,
                media_id=media_id,
                message="Instagram post published successfully.",
            ).model_dump()

    except Exception as e:
        logger.exception("Exception occurred during Instagram publishing")
        err_str = str(e)
        _record_post_status(db, image_url, full_caption, status="ERROR", error=err_str)
        return InstagramPublishResponse(
            success=False,
            message=f"Error connecting to Instagram API: {err_str}",
            error_code="NETWORK_ERROR",
        ).model_dump()


def publish_instagram_post(
    image_url: str,
    caption: str,
    hashtags: Optional[list[str]] = None,
    db: Optional[Session] = None,
) -> dict[str, Any]:
    """Synchronous wrapper for tool calls."""
    import asyncio

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # If running inside an async loop, run in separate thread to prevent blocking
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(
                asyncio.run,
                publish_instagram_post_async(image_url, caption, hashtags, db),
            )
            return future.result()
    else:
        return asyncio.run(publish_instagram_post_async(image_url, caption, hashtags, db))


def _record_post_status(
    db: Optional[Session],
    image_url: str,
    caption: str,
    status: str,
    media_id: Optional[str] = None,
    account_id: Optional[str] = None,
    error: Optional[str] = None,
) -> None:
    if db is None:
        return
    try:
        post = SocialPost(
            platform="instagram",
            platform_account_id=account_id,
            media_id=media_id,
            image_url=image_url,
            caption=caption,
            status=status,
            error=error,
        )
        db.add(post)
        db.commit()
    except Exception:
        logger.exception("Failed to record SocialPost in database")
        db.rollback()
