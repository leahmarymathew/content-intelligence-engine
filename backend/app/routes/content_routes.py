from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.content_model import Content
from app.schemas.content_schema import ContentRequest, ContentResponse
from app.webhooks.webhook_handlers import handle_content_created
from app.services.content_service import save_content
from app.services.categorization_service import categorize_content

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/generate-content", response_model=ContentResponse)
async def generate(request: ContentRequest, db: Session = Depends(get_db)) -> ContentResponse:
    # Generate structured content
    title = f"{request.topic} Content"
    summary = f"A {request.tone} piece of content about {request.topic} tailored for {request.audience} audience."
    content = f"""This is AI-generated content about {request.topic}.
    
Target Audience: {request.audience}
Tone: {request.tone}

This structured format allows for:
- Easy parsing and storage in databases
- Automated categorization
- Analytics on content components
- Building comprehensive content libraries"""
    
    # Build AI content object
    ai_content = {
        "title": title,
        "summary": summary,
        "content": content,
        "topic": request.topic,
        "audience": request.audience,
        "tone": request.tone
    }
    
    # Categorize the content
    category = await run_in_threadpool(categorize_content, title, content)
    
    # Save to database
    saved = await run_in_threadpool(save_content, db, ai_content, category)
    
    # Handle content creation event (webhooks, notifications, etc)
    await run_in_threadpool(handle_content_created, saved)
    
    return saved

@router.get("/content-library")
async def get_content_library(db: Session = Depends(get_db)) -> list[ContentResponse]:
    """Retrieve all content from the library"""
    contents = await run_in_threadpool(lambda: db.query(Content).all())
    return [
        ContentResponse(
            id=c.id,
            title=c.title,
            summary=c.summary,
            content=c.content,
            metadata={
                "topic": c.topic,
                "audience": c.audience,
                "tone": c.tone,
                "created_at": str(c.created_at)
            }
        )
        for c in contents
    ]

@router.get("/content/{content_id}", response_model=ContentResponse)
async def get_content(content_id: int, db: Session = Depends(get_db)) -> ContentResponse | dict[str, str]:
    db_content = await run_in_threadpool(lambda: db.query(Content).filter(Content.id == content_id).first())
    if not db_content:
        return {"error": "Content not found"}
    
    return ContentResponse(
        id=db_content.id,
        title=db_content.title,
        summary=db_content.summary,
        content=db_content.content,
        metadata={
            "topic": db_content.topic,
            "audience": db_content.audience,
            "tone": db_content.tone,
            "created_at": str(db_content.created_at)
        }
    )

@router.get("/content/topic/{topic}")
async def get_content_by_topic(topic: str, db: Session = Depends(get_db)) -> list[ContentResponse]:
    contents = await run_in_threadpool(lambda: db.query(Content).filter(Content.topic.ilike(f"%{topic}%")).all())
    return [
        ContentResponse(
            id=c.id,
            title=c.title,
            summary=c.summary,
            content=c.content,
            metadata={"topic": c.topic, "audience": c.audience, "tone": c.tone}
        )
        for c in contents
    ]