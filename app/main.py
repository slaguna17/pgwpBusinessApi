from app.config import WHATSAPP_VERIFY_TOKEN
from app.models import InvokeRequest, InvokeResponse
from app.services.agent_service import ensure_agent
from app.services.whatsapp_service import _extract_wa_message, _wa_mark_read, _wa_send_text
from fastapi import FastAPI, Body, Request, Query, HTTPException
from app.utils.logger import logger

from mangum import Mangum

# ========================
# FastAPI app
# ========================

app = FastAPI(
    title="Store Agent",
    description="API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
 
@app.get("/health")
def health():
    ok = True
    try:
        logger.info("Health check: OK")
    except Exception:
        ok = False
    return {"ok": ok}

@app.post("/invoke", response_model=InvokeResponse)
def invoke(req: InvokeRequest = Body(...)):
    executor = ensure_agent()
    result = executor.invoke({"input": req.input, "chat_history": req.chat_history or []})
    return InvokeResponse(message=result.get("output", ""), debug=None)

# Verificación del webhook (GET)
@app.get("/webhook")
def whatsapp_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        # Meta requiere devolver el challenge tal cual
        return int(hub_challenge) if (hub_challenge and hub_challenge.isdigit()) else (hub_challenge or "")
    raise HTTPException(status_code=403, detail="verification_failed")

# Recepción de mensajes (POST)
@app.post("/webhook")
async def whatsapp_webhook(req: Request):
    try:
        payload = await req.json()
    except Exception:
        payload = {}

    # Log (opcional)
    # print("Incoming webhook message:", json.dumps(payload, indent=2, ensure_ascii=False))

    extracted = _extract_wa_message(payload)
    text = extracted["text"]
    from_phone = extracted["from_phone"]
    message_id = extracted["message_id"]
    business_phone_id = extracted["business_phone_id"]
    
    print(f"REQUEST: {req}")

    # Si no hay texto (plantillas, media, etc.), ignoramos
    if not text or not from_phone:
        return {"status": "ignored"}

    # Ejecutar agente con tus tools (Store)
    executor = ensure_agent()
    result = executor.invoke({"input": text, "chat_history": []})
    bot_reply = result.get("output", "No pude generar una respuesta.")

    # Enviar respuesta por WhatsApp
    send_res = _wa_send_text(business_phone_id, from_phone, bot_reply, reply_to_message_id=message_id)

    # Marcar como leído
    if message_id:
        _ = _wa_mark_read(business_phone_id, message_id)

    return {"status": "ok", "agent_answer": bot_reply, "send_result": send_res}

# ========================
# Lambda adapter
# ========================
lambda_handler = Mangum(app)

# ============== Local Dev ==============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)