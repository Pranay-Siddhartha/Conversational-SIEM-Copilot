import json
import re
import urllib.request
import urllib.error
import os

from backend.config import settings
from backend.prompts.templates import (
    CHAT_SYSTEM_PROMPT,
    CHAT_USER_TEMPLATE,
    TIMELINE_PROMPT,
    PREDICTION_PROMPT,
    REPORT_PROMPT,
)


def _sanitize(text: str) -> str:
    """Strip control characters that break JSON serialization."""
    if not text:
        return text
    # Remove all control chars except tab, newline, carriage return
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)


def _safe_json_loads(raw: str) -> dict | None:
    """Extract and parse JSON from AI response, sanitizing control chars first."""
    json_match = re.search(r"\{[\s\S]*\}", raw)
    if not json_match:
        return None

    json_str = json_match.group()

    # First attempt: parse as-is
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # Second attempt: sanitize control characters then parse
    try:
        return json.loads(_sanitize(json_str))
    except json.JSONDecodeError:
        pass

    # Third attempt: encode/decode round-trip to normalize escaping
    try:
        normalized = json_str.encode('utf-8', errors='ignore').decode('utf-8')
        return json.loads(normalized)
    except json.JSONDecodeError:
        return None


def call_groq(system_prompt: str, user_prompt: str) -> str:
    """Call Groq API using lightweight urllib (Railway-safe)."""

    api_key = os.getenv("GROQ_API_KEY") or getattr(settings, "GROQ_API_KEY", None)
    print(f"DEBUG: Groq API initialized. Key present: {bool(api_key)}")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it in Railway/Vercel Project Settings → Environment Variables."
        )

    url = "https://api.groq.com/openai/v1/chat/completions"

    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 2048,
    })

    req = urllib.request.Request(
        url,
        data=payload.encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "SIEMCopilot/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)

            if "choices" not in data or not data["choices"]:
                raise RuntimeError(f"Unexpected Groq response: {raw[:300]}")

            return data["choices"][0]["message"]["content"]

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Groq API error: {body[:300]}")

    except urllib.error.URLError as e:
        raise RuntimeError(f"Groq network error: {str(e)}")

    except Exception as e:
        raise RuntimeError(f"Unexpected Groq failure: {str(e)}")


def generate_chat_response(question: str, log_context: str, count: int = 0) -> str:
    """Generate AI response for chat-based security investigation."""
    prompt = CHAT_USER_TEMPLATE.format(
        count=count,
        log_context=log_context,
        question=question,
    )
    return call_groq(CHAT_SYSTEM_PROMPT, prompt)


def generate_attack_story(events_text: str) -> dict:
    prompt = TIMELINE_PROMPT.format(events=events_text)
    raw = call_groq(CHAT_SYSTEM_PROMPT, prompt)

    parsed = _safe_json_loads(raw)
    if parsed:
        narrative = parsed.get("narrative", "")
        if isinstance(narrative, str):
            nested = _safe_json_loads(narrative)
            if nested:
                narrative = nested.get("narrative", narrative)
        return {
            "narrative": _sanitize(narrative),
            "overall_severity": _sanitize(str(parsed.get("overall_severity", "high"))),
        }

    # Last resort: if raw itself looks like a JSON blob, strip the wrapper manually
    narrative = raw
    json_key_match = re.search(r'"narrative"\s*:\s*"([\s\S]*?)",?\s*"overall_severity"', raw)
    if json_key_match:
        narrative = json_key_match.group(1)

    return {
        "narrative": _sanitize(narrative),
        "overall_severity": "high",
    }


def predict_next_move(timeline_text: str) -> dict:
    """Predict attacker next move from timeline."""
    prompt = PREDICTION_PROMPT.format(timeline=timeline_text)
    raw = call_groq(CHAT_SYSTEM_PROMPT, prompt)

    parsed = _safe_json_loads(raw)
    if parsed:
        # Sanitize all string values in the parsed dict
        return {k: _sanitize(v) if isinstance(v, str) else v for k, v in parsed.items()}

    # Fallback: return sanitized raw text
    return {
        "predicted_next_move": _sanitize(raw[:200]),
        "confidence": "medium",
        "reasoning": _sanitize(raw),
        "recommended_actions": [],
    }


def generate_report(incident_data: str) -> str:
    """Generate professional incident response report."""
    prompt = REPORT_PROMPT.format(incident_data=incident_data)
    return call_groq(CHAT_SYSTEM_PROMPT, prompt)