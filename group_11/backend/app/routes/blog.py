"""Blog generation endpoints."""

import logging

from fastapi import APIRouter, HTTPException

from app.models.blog import BlogGenerateRequest, BlogListItem, BlogPost
from app.services.blog_service import delete_blog, generate_blog, get_blog, list_blogs

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/blog", tags=["blog"])


@router.post("/generate", response_model=BlogPost)
async def generate(req: BlogGenerateRequest):
    """Generate a blog post from a topic (text + image + podcast)."""
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    if len(topic) > 200:
        raise HTTPException(status_code=400, detail="Topic must be under 200 characters")

    try:
        import asyncio
        blog = await asyncio.to_thread(generate_blog, topic)
        return BlogPost(**blog)
    except Exception as e:
        logger.exception("Blog generation failed")
        msg = str(e).lower()
        if "quota" in msg or "429" in msg:
            raise HTTPException(status_code=500, detail="AI service out of credits. Check your API billing.")
        if "401" in msg or "unauthorized" in msg:
            raise HTTPException(status_code=500, detail="AI API key is invalid. Check backend/.env.")
        raise HTTPException(status_code=500, detail=f"Blog generation failed: {str(e)[:200]}")


@router.get("", response_model=list[BlogListItem])
async def list_all():
    """List all generated blogs."""
    blogs = list_blogs()
    return [BlogListItem(**b) for b in blogs]


@router.get("/{blog_id}", response_model=BlogPost)
async def get_one(blog_id: str):
    """Get a single blog post."""
    blog = get_blog(blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return BlogPost(**blog)


@router.delete("/{blog_id}")
async def remove(blog_id: str):
    """Delete a blog and its assets."""
    if not delete_blog(blog_id):
        raise HTTPException(status_code=404, detail="Blog not found")
    return {"status": "deleted", "id": blog_id}
