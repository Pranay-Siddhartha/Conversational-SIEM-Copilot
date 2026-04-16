"""Analysis endpoints: timeline, predictions, risk scoring, threats."""
import json
import hashlib
import traceback
from collections import defaultdict
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.models import LogEvent, Incident
from backend.schemas import (
    TimelineResponse, TimelineEvent, PredictionResponse,
    RiskScoreResponse, AttackChain, AttackChainsResponse
)
from backend.ai.groq_client import generate_attack_story, predict_next_move
from backend.services.threat_detector import detect_threats
from backend.services.risk_scorer import calculate_risk_score
from backend.services.logger import get_logger, log_error

logger = get_logger("analysis")
router = APIRouter(prefix="/analysis", tags=["analysis"])

# ── IN-MEMORY CACHE ───────────────────────────────────────
# Stores AI results keyed by a hash of the events text.
# Cleared only when logs change (upload/clear).
# This prevents re-calling Groq on every page load/refresh.
_ai_cache: dict[str, dict] = {}


def _cache_key(prefix: str, text: str) -> str:
    """Generate a stable cache key from event text."""
    digest = hashlib.md5(text.encode()).hexdigest()
    return f"{prefix}:{digest}"


def _cached_generate_attack_story(events_text: str) -> dict:
    key = _cache_key("story", events_text)
    if key not in _ai_cache:
        logger.info(f"[cache miss] generate_attack_story — calling Groq")
        _ai_cache[key] = generate_attack_story(events_text)
    else:
        logger.info(f"[cache hit] generate_attack_story — skipping Groq call")
    return _ai_cache[key]


def _cached_predict_next_move(events_text: str) -> dict:
    key = _cache_key("pred", events_text)
    if key not in _ai_cache:
        logger.info(f"[cache miss] predict_next_move — calling Groq")
        _ai_cache[key] = predict_next_move(events_text)
    else:
        logger.info(f"[cache hit] predict_next_move — skipping Groq call")
    return _ai_cache[key]


def clear_ai_cache():
    """Call this whenever logs are uploaded or cleared."""
    _ai_cache.clear()
    logger.info("[cache] AI cache cleared")


# ── TIMELINE ─────────────────────────────────────────────

@router.get("/timeline", response_model=TimelineResponse)
def get_timeline(db: Session = Depends(get_db)):
    """Generate attack timeline from stored events."""
    events = (
        db.query(LogEvent)
        .order_by(LogEvent.timestamp.asc().nullslast())
        .all()
    )

    if not events:
        return TimelineResponse(
            events=[],
            ai_narrative="No log data available. Upload logs to generate a timeline.",
            overall_severity="info",
        )

    event_dicts = [_event_to_dict(e) for e in events]
    threats = detect_threats(event_dicts)

    timeline_events = []
    seen = set()
    for e in events:
        if e.severity in ("high", "critical") or e.status == "failure":
            ts_str = e.timestamp.strftime("%Y-%m-%d %H:%M:%S") if e.timestamp else "unknown"
            key = f"{ts_str}-{e.action}-{e.source_ip}"
            if key not in seen:
                seen.add(key)
                timeline_events.append(TimelineEvent(
                    timestamp=ts_str,
                    event=f"{e.action or 'event'} by {e.username or 'unknown'} from {e.source_ip or 'unknown'}",
                    severity=e.severity or "medium",
                    details=e.raw_line[:200] if e.raw_line else None,
                ))

    events_text = "\n".join(
        f"[{te.timestamp}] {te.event} (severity: {te.severity})"
        for te in timeline_events[:30]
    )

    try:
        story = _cached_generate_attack_story(events_text) if timeline_events else {}

        severities = [te.severity for te in timeline_events]
        if "critical" in severities: overall = "critical"
        elif "high" in severities: overall = "high"
        elif "medium" in severities: overall = "medium"
        else: overall = "low"

        return TimelineResponse(
            events=timeline_events[:50],
            ai_narrative=story.get("narrative", "No significant attack pattern detected."),
            overall_severity=story.get("overall_severity", overall),
        )
    except Exception as e:
        log_error(logger, "Failed to generate attack story", e)
        return JSONResponse(
            status_code=500,
            content={"error": "Attack story generation failure", "detail": str(e)}
        )


# ── PREDICTIONS ──────────────────────────────────────────

@router.get("/predictions", response_model=PredictionResponse)
def get_predictions(db: Session = Depends(get_db)):
    """Predict attacker's next move based on observed patterns."""
    events = db.query(LogEvent).order_by(LogEvent.timestamp.asc().nullslast()).all()

    if not events:
        return PredictionResponse(
            predicted_next_move="No data available for prediction.",
            confidence="low",
            reasoning="Upload security logs to enable threat prediction.",
            recommended_actions=["Upload security logs to get started"],
        )

    timeline_text = "\n".join(
        f"[{e.timestamp.strftime('%H:%M:%S') if e.timestamp else '??:??'}] "
        f"{e.action or 'event'} | user={e.username or '-'} | ip={e.source_ip or '-'} | status={e.status or '-'}"
        for e in events
        if e.severity in ("high", "critical") or e.status == "failure"
    )

    if not timeline_text:
        timeline_text = "No significant threats detected in current log data."

    try:
        result = _cached_predict_next_move(timeline_text)
        return PredictionResponse(
            predicted_next_move=result.get("predicted_next_move", "Unable to predict"),
            confidence=result.get("confidence", "medium"),
            reasoning=result.get("reasoning", ""),
            recommended_actions=result.get("recommended_actions", []),
        )
    except Exception as e:
        log_error(logger, "Failed to generate threat predictions", e)
        return JSONResponse(
            status_code=500,
            content={"error": "Threat prediction failure", "detail": str(e)}
        )


# ── RISK SCORE ───────────────────────────────────────────

@router.get("/risk-score", response_model=RiskScoreResponse)
def get_risk_score(db: Session = Depends(get_db)):
    """Calculate overall risk score."""
    events = db.query(LogEvent).all()

    if not events:
        return RiskScoreResponse(
            overall_score=0,
            severity="low",
            factors=[{"factor": "Empty Telemetry", "detail": "No log events available yet", "impact": 0}]
        )

    event_dicts = [_event_to_dict(e) for e in events]
    threats = detect_threats(event_dicts)
    result = calculate_risk_score(event_dicts, threats)

    return RiskScoreResponse(
        overall_score=result["overall_score"],
        severity=result["severity"],
        factors=result["factors"],
    )


# ── THREATS ──────────────────────────────────────────────

@router.get("/threats")
def get_threats(db: Session = Depends(get_db)):
    """Get detected threats from stored logs."""
    events = db.query(LogEvent).all()
    event_dicts = [_event_to_dict(e) for e in events]
    threats = detect_threats(event_dicts)
    return {"threats": threats, "count": len(threats)}


# ── ATTACK CHAINS ────────────────────────────────────────

@router.get("/chains", response_model=AttackChainsResponse)
def get_attack_chains(db: Session = Depends(get_db)):
    """Group suspicious events by source IP to create distinct attack chains."""
    events = db.query(LogEvent).order_by(LogEvent.timestamp.asc().nullslast()).all()
    if not events:
        return AttackChainsResponse(chains=[])

    # 1. Gather suspicious events by IP
    chains_dict = defaultdict(list)
    for e in events:
        if e.severity in ("high", "critical") or e.status == "failure" or (e.action and "escalat" in e.action.lower()):
            ip = e.source_ip or "unknown_ip"
            chains_dict[ip].append(e)

    # 2. Build chains
    attack_chains = []
    chain_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    idx = 0

    for ip, ip_events in chains_dict.items():
        if not ip_events:
            continue

        actions = [e.action for e in ip_events if e.action]
        primary_action = max(set(actions), key=actions.count) if actions else "Suspicious Activity"

        severities = [e.severity for e in ip_events]
        if "critical" in severities: severity = "critical"
        elif "high" in severities: severity = "high"
        elif "medium" in severities: severity = "medium"
        else: severity = "low"

        timeline_events = []
        seen = set()
        for e in ip_events:
            ts_str = e.timestamp.strftime("%Y-%m-%d %H:%M:%S") if e.timestamp else "unknown"
            key = f"{ts_str}-{e.action}"
            if key not in seen:
                seen.add(key)
                timeline_events.append(TimelineEvent(
                    timestamp=ts_str,
                    event=f"{e.action or 'event'} by {e.username or 'unknown'}",
                    severity=e.severity or "medium",
                    details=e.raw_line[:200] if e.raw_line else None,
                ))

        events_text = "\n".join(
            f"[{te.timestamp}] {te.event} from {ip} (severity: {te.severity})"
            for te in timeline_events[:30]
        )

        # ── CACHED AI CALLS (no repeat Groq hits on refresh) ──
        try:
            story = _cached_generate_attack_story(events_text) if timeline_events else {}
        except Exception as e:
            story = {"narrative": f"AI narrative error: {str(e)}"}

        try:
            pred_res = _cached_predict_next_move(events_text) if timeline_events else {}
        except Exception as e:
            pred_res = {
                "predicted_next_move": f"Prediction error: {str(e)}",
                "confidence": "low",
                "reasoning": "AI error.",
                "recommended_actions": []
            }

        prediction = PredictionResponse(
            predicted_next_move=pred_res.get("predicted_next_move", "Unknown"),
            confidence=pred_res.get("confidence", "low"),
            reasoning=pred_res.get("reasoning", ""),
            recommended_actions=pred_res.get("recommended_actions", [])
        )

        attack_chains.append(AttackChain(
            incident_name=f"Attack Chain {chain_letters[idx % len(chain_letters)]}",
            source_ip=ip,
            severity=severity,
            primary_attack_type=primary_action.replace("_", " ").title(),
            timeline=timeline_events[:50],
            ai_narrative=story.get("narrative", "Attack sequence detected."),
            prediction=prediction
        ))
        idx += 1

    severity_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    attack_chains.sort(
        key=lambda c: (severity_rank.get(c.severity.lower(), 0), len(c.timeline)),
        reverse=True
    )

    return AttackChainsResponse(chains=attack_chains)


# ── HELPERS ──────────────────────────────────────────────

def _event_to_dict(e: LogEvent) -> dict:
    return {
        "timestamp": e.timestamp,
        "source_ip": e.source_ip,
        "dest_ip": e.dest_ip,
        "username": e.username,
        "action": e.action,
        "status": e.status,
        "raw_line": e.raw_line,
        "severity": e.severity,
        "log_source": e.log_source,
    }