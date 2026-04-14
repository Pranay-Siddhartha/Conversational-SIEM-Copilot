"""Conversational AI chat endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.models import LogEvent
from backend.schemas import ChatRequest, ChatResponse
from backend.ai.groq_client import generate_chat_response
from backend.services.logger import get_logger, log_error

logger = get_logger("chat")
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    # ... logic stays same ...
    # Fetch recent events as context
    events = (
        db.query(LogEvent)
        .order_by(LogEvent.timestamp.desc().nullslast())
        .limit(req.context_limit)
        .all()
    )

    if not events:
        return ChatResponse(
            reply="No log data found. Please upload security logs first using the upload feature.",
            sources_used=0,
        )

    # Build text context from events
    context_lines = []
    for e in events:
        ts = e.timestamp.strftime("%Y-%m-%d %H:%M:%S") if e.timestamp else "unknown"
        line = (
            f"[{ts}] src={e.source_ip or '-'} user={e.username or '-'} "
            f"action={e.action or '-'} status={e.status or '-'} "
            f"severity={e.severity or '-'}"
        )
        if e.raw_line and len(e.raw_line) < 200:
            line += f" raw=\"{e.raw_line}\""
        context_lines.append(line)

    log_context = "\n".join(context_lines)

    try:
        reply = generate_chat_response(req.message, log_context, count=len(events))
        return ChatResponse(reply=reply, sources_used=len(events))
    except Exception as e:
        log_error(logger, "Failed to generate AI chat response", e)
        return JSONResponse(
            status_code=500,
            content={"error": "Investigation service failure", "detail": str(e)}
        )

