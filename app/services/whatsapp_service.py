
from typing import Any, Dict, Optional
import requests
from app.config import WHATSAPP_PHONE_ID, WHATSAPP_TOKEN

def _extract_wa_message(payload: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """
    Extrae campos clave del payload de WhatsApp Cloud:
    - text, from_phone, message_id, business_phone_id
    """
    text = from_phone = message_id = business_phone_id = None
    try:
        entry = payload.get("entry", [])[0]
        change = entry.get("changes", [])[0]
        value = change.get("value", {})
        messages = value.get("messages", [])
        metadata = value.get("metadata", {})
        business_phone_id = metadata.get("phone_number_id") or None
        if messages:
            m = messages[0]
            message_id = m.get("id")
            from_phone = m.get("from")
            if m.get("type") == "text":
                text = m.get("text", {}).get("body")
    except Exception:
        pass
    return {
        "text": text,
        "from_phone": from_phone,
        "message_id": message_id,
        "business_phone_id": business_phone_id
    }

def _wa_send_text(business_phone_id: str, to_phone: str, text: str, reply_to_message_id: Optional[str] = None) -> Dict[str, Any]:
    if not WHATSAPP_TOKEN:
        return {"warning": "WHATSAPP_TOKEN no configurado; no se envía respuesta."}
    target_id = business_phone_id or WHATSAPP_PHONE_ID
    if not target_id:
        return {"warning": "No hay phone_number_id (payload ni env var)."}
    url = f"https://graph.facebook.com/v18.0/{target_id}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": (text or "")[:4096]},
    }
    if reply_to_message_id:
        data["context"] = {"message_id": reply_to_message_id}
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return {"error": "wa_send_failed", "detail": str(e)}

def _wa_mark_read(business_phone_id: str, message_id: str) -> Dict[str, Any]:
    if not WHATSAPP_TOKEN:
        return {"warning": "WHATSAPP_TOKEN no configurado; no se marca como leído."}
    target_id = business_phone_id or WHATSAPP_PHONE_ID
    if not target_id:
        return {"warning": "No hay phone_number_id (payload ni env var)."}
    url = f"https://graph.facebook.com/v18.0/{target_id}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return {"error": "wa_mark_read_failed", "detail": str(e)}