import os
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv

from app.normalize import extract_text_messages
from app.policy import decide
from app.whatsapp import send_text

load_dotenv()

app = FastAPI()

VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "").strip()

@app.get("/health")
def health():
    return {"ok": True}

# Meta webhook verification (GET)
@app.get("/webhook")
def webhook_verify(request: Request):
    """
    Meta calls this during webhook setup:
      hub.mode=subscribe
      hub.verify_token=...
      hub.challenge=...
    We must echo hub.challenge if verify_token matches.
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN and challenge:
        return int(challenge)

    raise HTTPException(status_code=403, detail="Verification failed")

# Incoming messages (POST)
@app.post("/webhook")
async def webhook_receive(request: Request):
    payload = await request.json()

    # Normalize inbound text messages
    messages = extract_text_messages(payload)

    # If no relevant messages, just ack
    if not messages:
        return {"status": "ignored"}

    for msg in messages:
        from_number = msg["from"]          # usually digits-only like "14155551234"
        text = msg["text"]

        decision = decide(from_number=normalize_number(from_number), text=text)

        # Only message you: enforced by allowlist in policy.py
        if not decision.allowed or decision.action == "block":
            continue

        # V1 behavior: draft reply (no LLM yet) + optionally send if MODE=send
        draft = build_draft_reply(text=text, reasons=decision.reasons)

        if decision.action == "send":
            # Send back to same number (you)
            resp = send_text(to_number=from_number, message=draft)
            # Optional: log resp.status_code, resp.text
        else:
            # draft_only: do nothing, but you could log the draft somewhere
            pass

    return {"status": "ok"}

def normalize_number(n: str) -> str:
    """
    WhatsApp webhook 'from' is often digits-only. Your allowlist may be E.164.
    For v1, we normalize by:
      - if allowlist uses +1... keep that format
      - if 'from' is digits-only, convert US '1XXXXXXXXXX' to '+1XXXXXXXXXX' if length 11 startswith 1
    Adjust as needed for your country.
    """
    n = (n or "").strip()
    if n.startswith("+"):
        return n
    if len(n) == 11 and n.startswith("1"):
        return "+" + n
    return n

def build_draft_reply(text: str, reasons: list[str]) -> str:
    """
    Placeholder. Later you’ll swap this with an LLM draft + policy checks.
    """
    if reasons:
        return (
            "Draft-only: I received your message, but flagged it as potentially risky.\n"
            f"Reasons: {', '.join(reasons)}\n"
            "If you want me to act on it, confirm explicitly."
        )

    return (
        "Draft-only: got it. ✅\n"
        f"You said: {text}\n"
        "Reply with 'CONFIRM' if you want me to send an automated response."
    )
