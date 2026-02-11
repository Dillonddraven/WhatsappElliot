import os
import requests
from typing import Optional

GRAPH_BASE = "https://graph.facebook.com/v21.0"

def send_text(to_number: str, message: str) -> requests.Response:
    """
    Sends a WhatsApp text message via Meta Cloud API.
    `to_number` must be in international format digits only or E.164 depending on your setup.
    (Meta typically expects digits-only; webhook 'from' is digits-only.)
    """
    token = os.getenv("WHATSAPP_ACCESS_TOKEN", "").strip()
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "").strip()
    if not token or not phone_number_id:
        raise RuntimeError("Missing WHATSAPP_ACCESS_TOKEN or WHATSAPP_PHONE_NUMBER_ID in env.")

    url = f"{GRAPH_BASE}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message},
    }
    return requests.post(url, headers=headers, json=data, timeout=20)
