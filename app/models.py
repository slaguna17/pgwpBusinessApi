from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class InvokeRequest(BaseModel):
    input: str = Field(..., description="Instrucción del usuario")
    chat_history: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Historial de chat compatible con LangChain Messages"
    )

class InvokeResponse(BaseModel):
    message: str
    debug: Optional[Dict[str, Any]] = None