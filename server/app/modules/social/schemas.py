from __future__ import annotations

"""Pydantic schemas for Social Media Agent & Instagram Publishing."""


from pydantic import BaseModel, Field


class InstagramPublishRequest(BaseModel):
    image_url: str = Field(
        ..., description="Publicly accessible HTTP/HTTPS URL of the image to post"
    )
    caption: str = Field(..., description="The main text caption for the Instagram post")
    hashtags: list[str] = Field(
        default_factory=list, description="List of hashtags to include with the post"
    )


class InstagramPublishResponse(BaseModel):
    success: bool
    platform: str = "instagram"
    media_id: str | None = None
    message: str
    error_code: str | None = None
