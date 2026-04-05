"""
Blog generation service — orchestrates LLM text, image, and TTS.
All generated assets stored in backend/app/data/blogs/{blog_id}/
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.settings import get_settings

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_BLOGS_DIR = _DATA_DIR / "blogs"
_BLOGS_INDEX = _DATA_DIR / "blogs.json"

BLOG_SYSTEM_PROMPT = """\
You are a financial tips writer. Given a topic, write a short, actionable tip.

Rules:
- Title on the first line prefixed with "TITLE: "
- Then a blank line
- Then the tip body (2-3 short paragraphs)
- STRICT LIMIT: keep the total tip under 100 words
- Write in a clear, engaging, conversational tone
- Focus on practical, actionable advice
- Do NOT use markdown headers or formatting — plain text only
"""

IMAGE_PROMPT_TEMPLATE = """\
Given this blog topic: "{topic}"
Write a single short image description (under 15 words) suitable for generating \
a blog featured image. Just the description, nothing else."""


def _get_llm() -> ChatOpenAI:
    settings = get_settings()
    if settings.llm_provider == "openrouter" and settings.openrouter_api_key:
        return ChatOpenAI(
            model=settings.openrouter_model,
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            temperature=0.7,
            default_headers={
                "HTTP-Referer": "https://demoai-one.vercel.app",
                "X-Title": "DemoAI Blog",
            },
        )
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.7,
    )


def _ensure_dirs():
    _BLOGS_DIR.mkdir(parents=True, exist_ok=True)
    if not _BLOGS_INDEX.exists():
        _BLOGS_INDEX.write_text("[]", encoding="utf-8")


def _load_index() -> list[dict]:
    _ensure_dirs()
    return json.loads(_BLOGS_INDEX.read_text(encoding="utf-8"))


def _save_index(blogs: list[dict]):
    _BLOGS_INDEX.write_text(json.dumps(blogs, indent=2, default=str), encoding="utf-8")


# ── Text Generation ──────────────────────────────────────────


def generate_blog_text(topic: str) -> tuple[str, str]:
    """Generate blog title + content from a topic. Returns (title, content)."""
    llm = _get_llm()
    response = llm.invoke([
        SystemMessage(content=BLOG_SYSTEM_PROMPT),
        HumanMessage(content=f"Write a blog post about: {topic}"),
    ])
    text = response.content if isinstance(response.content, str) else str(response.content)

    # Parse title from first line
    lines = text.strip().split("\n")
    title = topic  # fallback
    content_lines = lines

    for i, line in enumerate(lines):
        if line.strip().upper().startswith("TITLE:"):
            title = line.split(":", 1)[1].strip()
            content_lines = lines[i + 1:]
            break

    content = "\n".join(content_lines).strip()
    return title, content


# ── Image Generation ─────────────────────────────────────────


def generate_blog_image(topic: str, blog_id: str) -> str | None:
    """Generate a featured image. Returns relative URL path or None."""
    settings = get_settings()
    blog_dir = _BLOGS_DIR / blog_id
    blog_dir.mkdir(parents=True, exist_ok=True)
    image_path = blog_dir / "image.png"

    try:
        # Get a short image description from LLM
        llm = _get_llm()
        desc_response = llm.invoke([
            HumanMessage(content=IMAGE_PROMPT_TEMPLATE.format(topic=topic)),
        ])
        description = desc_response.content if isinstance(desc_response.content, str) else str(desc_response.content)
        description = description.strip().strip('"')

        # Use Pollinations.ai (free, no API key)
        encoded = description.replace(" ", "%20")
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=400&nologo=true"

        with httpx.Client(timeout=30.0) as client:
            resp = client.get(image_url, follow_redirects=True)
            if resp.status_code == 200 and len(resp.content) > 1000:
                image_path.write_bytes(resp.content)
                logger.info("Image saved: %s", image_path)
                return f"/media/blogs/{blog_id}/image.png"

        logger.warning("Image generation returned unexpected response")
        return None

    except Exception as e:
        logger.warning("Image generation failed: %s", e)
        return None


# ── Text-to-Speech ───────────────────────────────────────────


def generate_podcast(content: str, blog_id: str) -> str | None:
    """Convert blog text to MP3 audio. Returns relative URL path or None."""
    blog_dir = _BLOGS_DIR / blog_id
    blog_dir.mkdir(parents=True, exist_ok=True)
    audio_path = blog_dir / "podcast.mp3"

    try:
        from gtts import gTTS

        tts = gTTS(text=content, lang="en", slow=False)
        tts.save(str(audio_path))
        logger.info("Podcast saved: %s", audio_path)
        return f"/media/blogs/{blog_id}/podcast.mp3"

    except Exception as e:
        logger.warning("TTS generation failed: %s", e)
        return None


# ── Full Pipeline ────────────────────────────────────────────


def generate_blog(topic: str) -> dict:
    """Full blog generation: text + image + podcast. Returns blog dict."""
    _ensure_dirs()
    blog_id = str(uuid.uuid4())[:8]
    now = datetime.now(timezone.utc).isoformat()

    # 1. Generate text
    title, content = generate_blog_text(topic)

    # 2. Generate image
    image_url = generate_blog_image(topic, blog_id)

    # 3. Generate podcast
    audio_url = generate_podcast(content, blog_id)

    # 4. Save to index
    blog = {
        "id": blog_id,
        "topic": topic,
        "title": title,
        "content": content,
        "image_url": image_url,
        "audio_url": audio_url,
        "created_at": now,
    }

    # Save content as text file too
    blog_dir = _BLOGS_DIR / blog_id
    blog_dir.mkdir(parents=True, exist_ok=True)
    (blog_dir / "content.txt").write_text(f"{title}\n\n{content}", encoding="utf-8")

    blogs = _load_index()
    blogs.insert(0, blog)  # newest first
    _save_index(blogs)

    return blog


def list_blogs() -> list[dict]:
    """Return all blogs (newest first)."""
    return _load_index()


def get_blog(blog_id: str) -> dict | None:
    """Get a single blog by ID."""
    blogs = _load_index()
    return next((b for b in blogs if b["id"] == blog_id), None)


def delete_blog(blog_id: str) -> bool:
    """Delete a blog and its assets."""
    import shutil

    blogs = _load_index()
    updated = [b for b in blogs if b["id"] != blog_id]
    if len(updated) == len(blogs):
        return False

    _save_index(updated)

    blog_dir = _BLOGS_DIR / blog_id
    if blog_dir.exists():
        shutil.rmtree(blog_dir)

    return True
