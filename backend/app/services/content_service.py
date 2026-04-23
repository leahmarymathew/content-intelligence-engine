from sqlalchemy.orm import Session
from app.models.content_model import Content
from app.schemas.content_schema import ContentResponse


def save_content(db: Session, data: dict, category: str) -> ContentResponse:
    """Persist generated content and return a normalized API response."""
    
    item = Content(
        title=data.get("title"),
        summary=data.get("summary"),
        content=data.get("content"),
        topic=data.get("topic"),
        audience=data.get("audience"),
        tone=data.get("tone"),
        category=category,
        keywords=None
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    # Return as ContentResponse
    return ContentResponse(
        id=item.id,
        title=item.title,
        summary=item.summary,
        content=item.content,
        metadata={
            "topic": item.topic,
            "audience": item.audience,
            "tone": item.tone,
            "category": item.category,
            "created_at": str(item.created_at)
        }
    )