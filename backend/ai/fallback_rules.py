"""Deterministic security analysis rules for when LLM is unavailable or for simple queries."""
from collections import Counter
import re

def analyze_logs_fallback(question: str, log_context: str) -> str:
    """Deterministic analysis from actual log data."""
    lines = log_context.strip().split("\n")
    q = question.lower()

    # Simple heuristic parser
    events = []
    for line in lines:
        event = {}
        for part in line.split():
            if part.startswith("src="): event["ip"] = part[4:]
            elif part.startswith("status="): event["status"] = part[7:]
            elif part.startswith("severity="): event["severity"] = part[9:]
        events.append(event)

    total = len(events)
    failures = [e for e in events if e.get("status") == "failure"]
    
    if "suspicious" in q or "threat" in q:
        fail_ips = Counter(e.get("ip", "unknown") for e in failures)
        result = "## 🔍 Deterministic Risk Analysis\n\n"
        result += f"Analyzed {total} events. Detected {len(failures)} failures.\n\n"
        if fail_ips:
            result += "### Top Offending IPs\n"
            for ip, count in fail_ips.most_common(5):
                result += f"- `{ip}`: {count} attempts\n"
        return result
    
    return f"Automated Summary: {total} security events analyzed. {len(failures)} failures detected."
