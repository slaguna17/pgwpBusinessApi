import os
from dotenv import load_dotenv

ENV = os.getenv("ENV", "local")  # en AWS define ENV=lambda

if ENV != "lambda":
    load_dotenv()
    print("🔹 Variables cargadas desde .env (entorno local)")
else:
    print("🔹 Ejecutando en entorno AWS Lambda (sin .env)")

# =========================
# 3️⃣ Variables críticas (falla si no existen)
# =========================
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
WHATSAPP_TOKEN  = os.environ["WHATSAPP_TOKEN"]
WHATSAPP_VERIFY_TOKEN = os.environ["WHATSAPP_VERIFY_TOKEN"]
TUKIOSCO_BASE_URL = os.environ["TUKIOSCO_BASE_URL"]
TUKIOSCO_EMAIL = os.environ["TUKIOSCO_EMAIL"]
TUKIOSCO_PASSWORD = os.environ["TUKIOSCO_PASSWORD"]

# =========================
# 4️⃣ Variables opcionales (con valores por defecto)
# =========================
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")