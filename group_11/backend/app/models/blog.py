"""Blog models."""

from pydantic import BaseModel


class BlogGenerateRequest(BaseModel):
    topic: str


class BlogPost(BaseModel):
    id: str
    topic: str
    title: str
    content: str
    image_url: str | None = None
    audio_url: str | None = None
    created_at: str


class BlogListItem(BaseModel):
    id: str
    title: str
    topic: str
    image_url: str | None = None
    created_at: str
