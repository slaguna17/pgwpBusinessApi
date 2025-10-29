import json
from typing import Optional, Dict, Any, List
from langchain.tools import tool
from app.services.store_service import _ensure_tk_token, tk_login_user_info, tk_products_list, tk_product_by_id, tk_sales_create, tk_cashbox_current, tk_call

@tool("tk_force_relogin", return_direct=False)
def tk_force_relogin() -> str:
    """Fuerza relogin en TuKiosco y refresca el JWT (el valor real no se expone)."""
    try:
        _ensure_tk_token(force=True)
        return json.dumps({"ok": True, "message": "Relogin TuKiosco exitoso"})
    except Exception as e:
        return json.dumps({"ok": False, "error": str(e)})

@tool("tk_me", return_direct=False)
def tk_me() -> str:
    """Devuelve la info del usuario asociada al token actual."""
    return json.dumps(tk_login_user_info())

@tool("tk_products", return_direct=False)
def tk_products() -> str:
    """Lista todos los productos."""
    return json.dumps(tk_products_list())

@tool("tk_product_by_id", return_direct=False)
def tk_product_by_id_tool(product_id: int) -> str:
    """Obtiene un producto por ID."""
    return json.dumps(tk_product_by_id(product_id))

@tool("tk_sales_create", return_direct=False)
def tk_sales_create_tool(
    store_id: int,
    user_id: int,
    products: List[Dict[str, Any]],
    payment_method: str = "cash",
    notes: Optional[str] = None
) -> str:
    """
    Crea una venta. products: [{product_id, quantity, unit_price}, ...]
    """
    payload = {
        "store_id": store_id,
        "user_id": user_id,
        "products": products,
        "payment_method": payment_method
    }
    if notes:
        payload["notes"] = notes
    return json.dumps(tk_sales_create(payload))

@tool("tk_cashbox_current", return_direct=False)
def tk_cashbox_current_tool(store_id: int) -> str:
    """Estado actual de la caja para una tienda."""
    return json.dumps(tk_cashbox_current(store_id))

@tool("tk_raw", return_direct=False)
def tk_raw(method: str, path: str, params_json: Optional[str] = None, body_json: Optional[str] = None) -> str:
    """
    Llamada cruda a cualquier endpoint (útil para nuevos recursos).
    method: GET|POST|PUT|DELETE
    path: e.g. '/products/categories/2/stores/1'
    params_json/body_json: JSON string con pares clave-valor.
    """
    try:
        params = json.loads(params_json) if params_json else None
        body = json.loads(body_json) if body_json else None
    except json.JSONDecodeError as e:
        return json.dumps({"error": "JSON inválido", "detail": str(e)})
    data = tk_call(method, path, params=params, json_body=body)
    return json.dumps(data)
