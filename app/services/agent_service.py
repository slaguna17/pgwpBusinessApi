# app/services/agent_service.py
from typing import Optional

from app.config import OPENAI_API_KEY, OPENAI_MODEL
# Si tu servicio de tienda tiene un "ensure token", impórtalo aquí.
# Renombré a _ensure_store_token por coherencia; si tu función actual
# aún se llama _ensure_moodle_token, puedes dejar ese nombre o crear un alias.

from app.tools.store_tools import (
    tk_force_relogin,
    tk_me,
    tk_products,
    tk_product_by_id_tool,
    tk_sales_create_tool,
    tk_cashbox_current_tool,
    tk_raw,
)

from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent  # 0.2.x
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# ========================
# Herramientas del Store
# ========================
STORE_TOOLS = [
    tk_force_relogin,
    tk_me,
    tk_products,
    tk_product_by_id_tool,
    tk_sales_create_tool,
    tk_cashbox_current_tool,
    tk_raw,
]

# ========================
# Prompt del Agente (Store)
# ========================
SYSTEM_PROMPT = """Eres un asistente de ventas integrado con el sistema de Tienda.
Reglas:
- Usa las herramientas disponibles del Store para responder sobre usuario actual (perfil), productos, caja y ventas.
- Para obtener información del usuario autenticado: tk_me.
- Para listar productos o buscar por nombre: tk_products.
- Para obtener detalles por ID de producto: tk_product_by_id_tool.
- Para crear una venta: tk_sales_create_tool (valida que existan productos y cantidades).
- Para ver el estado de caja actual: tk_cashbox_current_tool.
- Para llamadas avanzadas no cubiertas: tk_raw (describe con precisión qué endpoint y payload necesitas).
- Si alguna llamada devuelve 'invalidtoken' el sistema reintenta automáticamente con relogin mediante tk_force_relogin.
- Siempre responde en español, de forma clara, concisa y con pasos si la acción cambia estado (por ejemplo, crear una venta).
- Si te piden algo fuera del alcance de las herramientas, explícalo y sugiere la herramienta o los datos necesarios.
"""

# ========================
# Construcción del Agente
# ========================
def build_agent() -> AgentExecutor:
    if not OPENAI_API_KEY:
        raise RuntimeError("Falta OPENAI_API_KEY en variables de entorno.")

    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        temperature=0.2,
        api_key=OPENAI_API_KEY,
        timeout=40,
        max_retries=2,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, STORE_TOOLS, prompt)

    # Nota: puedes activar verbose=True en desarrollo para ver los pasos.
    executor = AgentExecutor(
        agent=agent,
        tools=STORE_TOOLS,
        verbose=False,
        handle_parsing_errors=True,  # más robusto ante respuestas parciales del modelo
    )
    return executor


AGENT_EXECUTOR: Optional[AgentExecutor] = None

def ensure_agent() -> AgentExecutor:
    """
    Inicializa el agente en singleton y hace un ensure opcional del token del Store.
    """
    global AGENT_EXECUTOR
    if AGENT_EXECUTOR is None:
        # Login de arranque (opcional; puedes diferir al primer uso real)
        try:
            print('hi')
            #_ensure_store_token(force=False)
        except TypeError:
            # En caso de que tu función antigua no acepte 'force', reintenta sin args
            print('hi')
            #_ensure_store_token()
        AGENT_EXECUTOR = build_agent()
    return AGENT_EXECUTOR
