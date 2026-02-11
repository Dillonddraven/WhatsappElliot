import os
import re
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class PolicyDecision:
    allowed: bool
    action: str  # "draft" | "send" | "block"
    reasons: List[str]

def _parse_allowlist() -> List[str]:
    raw = os.getenv("ALLOWLIST_NUMBERS", "").strip()
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]

INJECTION_PATTERNS = [
    r"ignore (all|any) (previous|prior) instructions",
    r"system prompt",
    r"developer message",
    r"reveal (secrets|tokens|keys|credentials)",
    r"send (me|us) your (token|api key|password)",
    r"click (this|the) link",
    r"download (this|the) file",
]

def decide(from_number: str, text: str) -> PolicyDecision:
    reasons: List[str] = []
    allowlist = _parse_allowlist()
    mode = os.getenv("MODE", "draft_only").strip().lower()

    if allowlist and from_number not in allowlist:
        return PolicyDecision(
            allowed=False,
            action="block",
            reasons=[f"Sender {from_number} not in allowlist."]
        )

    # Basic injection / risky intent heuristics (v1)
    lowered = (text or "").lower()
    for pat in INJECTION_PATTERNS:
        if re.search(pat, lowered):
            reasons.append(f"Matched risk pattern: {pat}")

    if reasons:
        # If anything looks like prompt injection, never auto-send
        return PolicyDecision(allowed=True, action="draft", reasons=reasons)

    # Default behavior
    if mode == "send":
        return PolicyDecision(allowed=True, action="send", reasons=["MODE=send"])
    return PolicyDecision(allowed=True, action="draft", reasons=["MODE=draft_only"])
