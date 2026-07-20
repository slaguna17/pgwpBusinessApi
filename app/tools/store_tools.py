import json
from typing import Optional, Dict, Any, List
from langchain.tools import tool
from app.services.store_service import (
    _ensure_tk_token, 
    tk_login_user_info, 
    tk_products_list, 
    tk_product_by_id,
    tk_cashbox_current,
    tk_stores_list,
    tk_store_by_id,
    tk_call,
    tk_shopping_carts_by_store,
    tk_shopping_cart_create,
    tk_shopping_cart_update,
    tk_shopping_cart_delete,
)

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

@tool("tk_cashbox_current", return_direct=False)
def tk_cashbox_current_tool(store_id: int) -> str:
    """Estado actual de la caja para una tienda."""
    return json.dumps(tk_cashbox_current(store_id))

@tool("tk_stores", return_direct=False)
def tk_stores() -> str:
    """Lista todas las tiendas."""
    return json.dumps(tk_stores_list())

@tool("tk_store_by_id", return_direct=False)
def tk_store_by_id_tool(store_id: int) -> str:
    """Obtiene una tienda por ID."""
    return json.dumps(tk_store_by_id(store_id))

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


# === Shopping Cart Tools ===

@tool("tk_cart_list_by_store", return_direct=False)
def tk_cart_list_by_store(store_id: int) -> str:
    """
    Lista los carritos de una tienda específica.
    Usa GET /shoppingCart/store/{storeId}.
    """
    data = tk_shopping_carts_by_store(store_id)
    return json.dumps(data)


@tool("tk_cart_create", return_direct=False)
def tk_cart_create(
    store_id: int,
    customer_phone: str,
    customer_name: str,
    items: List[Dict[str, Any]],
) -> str:
    """
    Crea un nuevo carrito de compras.

    items: lista de objetos con la forma:
      [
        {"product_id": 1, "quantity": 2, "unit_price": 20.0},
        {"product_id": 2, "quantity": 1, "unit_price": 5.0}
      ]

    IMPORTANTE: El agente debe asegurarse de que product_id, quantity y unit_price sean válidos.
    """
    payload = {
        "store_id": store_id,
        "customer_phone": customer_phone,
        "customer_name": customer_name,
        "items": items,
    }
    data = tk_shopping_cart_create(payload)
    return json.dumps(data)


@tool("tk_cart_update", return_direct=False)
def tk_cart_update(
    cart_id: int,
    store_id: int,
    customer_phone: str,
    customer_name: str,
    items: List[Dict[str, Any]],
) -> str:
    """
    Actualiza un carrito existente.

    Este endpoint reemplaza la lista completa de items del carrito.
    Por lo tanto, para "agregar" o "eliminar" productos, el agente debe:
      1. Conocer el estado actual de los items del carrito (por contexto o llamada previa).
      2. Construir la nueva lista de items final (con los cambios deseados).
      3. Enviar esa lista completa en 'items'.

    items: lista de objetos con la forma:
      [
        {"product_id": 1, "quantity": 3, "unit_price": 20.0},
        ...
      ]
    """
    payload = {
        "store_id": store_id,
        "customer_phone": customer_phone,
        "customer_name": customer_name,
        "items": items,
    }
    data = tk_shopping_cart_update(cart_id, payload)
    return json.dumps(data)


@tool("tk_cart_delete", return_direct=False)
def tk_cart_delete(cart_id: int) -> str:
    """
    Elimina un carrito por su ID.
    """
    data = tk_shopping_cart_delete(cart_id)
    return json.dumps(data)


