# Elliot WhatsApp (Meta Cloud API) - v1

## What this does
- Exposes a webhook endpoint for WhatsApp Cloud API
- Normalizes inbound text messages
- Applies strict policy (allowlist + draft_only)
- Optionally replies if MODE=send

## Setup (when you’re back at Elliot’s machine)
1) Create a venv + install deps
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
