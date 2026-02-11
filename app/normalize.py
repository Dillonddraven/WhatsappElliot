from typing import Any, Dict, List, Optional

def extract_text_messages(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Returns a list of normalized inbound text messages:
      [{"from": "+1...", "text": "hi", "wamid": "..."}]
    Works with typical WhatsApp Cloud API webhook payloads.
    """
    out: List[Dict[str, str]] = []
    entry = payload.get("entry", [])
    for e in entry:
        changes = e.get("changes", [])
        for c in changes:
            value = c.get("value", {})
            messages = value.get("messages", [])
            for m in messages:
                mtype = m.get("type")
                if mtype != "text":
                    continue
                out.append({
                    "from": m.get("from", ""),
                    "text": (m.get("text", {}) or {}).get("body", "") or "",
                    "wamid": m.get("id", ""),
                })
    return out
