import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.content_model import Content
from app.schemas.content_schema import ContentRequest, ContentResponse
from app.services.categorization_service import categorize_content
from app.services.content_service import save_content
from app.webhooks.webhook_handlers import handle_content_created

logger = logging.getLogger(__name__)
router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _call_groq(request: ContentRequest) -> dict:
    """Call Groq via the OpenAI-compatible SDK. Raises HTTPException on failure."""
    from openai import OpenAI

    api_key = settings.GROQ_API_KEY
    if not api_key or len(api_key) < 10:
        raise HTTPException(
            status_code=503,
            detail=(
                "Groq API key is not configured. "
                "Get a free key at console.groq.com, then add GROQ_API_KEY=gsk_... "
                "to backend/.env and restart the server."
            ),
        )

    content_type = request.contentType or "Blog Post"

    system_prompt = (
        "You are a world-class B2B content strategist and writer with 15 years of experience. "
        "You write content that feels like it came from a human subject-matter expert, not an AI. "
        "Your writing is specific, concrete, and immediately actionable. "
        "You never use filler phrases like 'In today's rapidly evolving landscape', 'it's more important than ever', "
        "'In conclusion', or 'As we navigate'. Every sentence earns its place. "
        "Always respond with valid JSON only — no markdown, no code fences, no extra text. "
        "The JSON must have exactly three keys: title, summary, content."
    )

    format_guide = {
        "Blog Post": "Use 3-5 H2 sections with ##. Each section must have 2-3 specific paragraphs. Include a concrete example or data point in at least 2 sections.",
        "Email Campaign": "Write a complete email: subject line as title, preview text as summary, full email body as content. Use short paragraphs (1-3 sentences). One clear CTA at the end.",
        "Social Media Post": "Write a punchy post optimised for engagement. Hook in the first line. Use line breaks for readability. Include 3-5 relevant hashtags at the end.",
        "Case Study": "Structure: Challenge → Approach → Results → Quote. Make the results specific (percentages, timeframes, dollar amounts). Write as a narrative, not a list.",
        "Newsletter": "Write a complete newsletter with a strong opener, 2-3 curated insights with commentary, and a closing thought. Conversational but substantive.",
        "Product Description": "Focus on outcomes, not features. Address the main objection. Include social proof language. End with a specific CTA.",
        "Landing Page Copy": "Headline + subheadline + 3 benefit sections + social proof element + CTA. Benefits must be outcome-focused, not feature-focused.",
    }.get(content_type, "Use clear headings and structured paragraphs. Minimum 3 distinct sections.")

    user_prompt = f"""Write a {content_type} with the following parameters:

Topic: {request.topic}
Target audience: {request.audience}
Tone: {request.tone}

Format requirements: {format_guide}

Return a JSON object with exactly these keys:
- "title": A specific, compelling title — no generic phrasing, no 'The Ultimate Guide to' or 'Everything You Need to Know'. Make it specific to this exact topic and audience.
- "summary": 1-2 sentences that describe exactly what this piece covers and what the reader will get from it. Be specific.
- "content": Minimum 350 words. Follow the format requirements above. Use real examples, specific numbers, and concrete scenarios relevant to {request.audience}. No padding, no repetition."""

    # Groq is OpenAI-API-compatible — point the openai SDK at Groq's endpoint
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("Groq returned invalid JSON: %s", raw[:300])
        raise HTTPException(status_code=500, detail=f"Groq returned malformed JSON: {exc}")


@router.post("/generate-content", response_model=ContentResponse)
async def generate(request: ContentRequest, db: Session = Depends(get_db)) -> ContentResponse:
    generated = await run_in_threadpool(_call_groq, request)

    title   = generated.get("title",   f"{request.topic} — {request.contentType or 'Content'}")
    summary = generated.get("summary", "")
    content = generated.get("content", "")

    if not content:
        raise HTTPException(status_code=500, detail="Groq returned empty content. Please try again.")

    ai_content = {
        "title":    title,
        "summary":  summary,
        "content":  content,
        "topic":    request.topic,
        "audience": request.audience,
        "tone":     request.tone,
    }

    category = await run_in_threadpool(categorize_content, title, content)
    saved    = await run_in_threadpool(save_content, db, ai_content, category)
    await run_in_threadpool(handle_content_created, saved)

    return saved


@router.get("/content-library")
async def get_content_library(db: Session = Depends(get_db)) -> list[ContentResponse]:
    contents = await run_in_threadpool(lambda: db.query(Content).all())
    return [
        ContentResponse(
            id=c.id,
            title=c.title,
            summary=c.summary,
            content=c.content,
            category=c.category,
            metadata={
                "topic":      c.topic,
                "audience":   c.audience,
                "tone":       c.tone,
                "created_at": str(c.created_at),
            },
        )
        for c in contents
    ]


@router.get("/content/{content_id}", response_model=ContentResponse)
async def get_content(content_id: int, db: Session = Depends(get_db)) -> ContentResponse:
    db_content = await run_in_threadpool(
        lambda: db.query(Content).filter(Content.id == content_id).first()
    )
    if not db_content:
        raise HTTPException(status_code=404, detail="Content not found")

    return ContentResponse(
        id=db_content.id,
        title=db_content.title,
        summary=db_content.summary,
        content=db_content.content,
        category=db_content.category,
        metadata={
            "topic":      db_content.topic,
            "audience":   db_content.audience,
            "tone":       db_content.tone,
            "created_at": str(db_content.created_at),
        },
    )


@router.get("/content/topic/{topic}")
async def get_content_by_topic(topic: str, db: Session = Depends(get_db)) -> list[ContentResponse]:
    contents = await run_in_threadpool(
        lambda: db.query(Content).filter(Content.topic.ilike(f"%{topic}%")).all()
    )
    return [
        ContentResponse(
            id=c.id,
            title=c.title,
            summary=c.summary,
            content=c.content,
            metadata={"topic": c.topic, "audience": c.audience, "tone": c.tone},
        )
        for c in contents
    ]
