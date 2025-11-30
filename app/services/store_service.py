import time
from typing import Any, Dict, Optional
import requests
from requests.adapters import HTTPAdapter, Retry
from app.config import TUKIOSCO_BASE_URL, TUKIOSCO_EMAIL, TUKIOSCO_PASSWORD

# Cache simple en proceso
_TK_TOKEN: Optional[str] = None
_TK_TOKEN_TS: Optional[float] = None  # opcional para TTL
_TK_SESSION: Optional[requests.Session] = None

def _session() -> requests.Session:
    global _TK_SESSION
    if _TK_SESSION is None:
        s = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
        )
        s.mount("http://", HTTPAdapter(max_retries=retries))
        s.mount("https://", HTTPAdapter(max_retries=retries))
        _TK_SESSION = s
    return _TK_SESSION

def _tk_login() -> str:
    """
    POST /users/login  -> {"token": "..."} (según tu backend)
    Body: {"email": "...", "password": "..."}
    """
    if not (TUKIOSCO_BASE_URL and TUKIOSCO_EMAIL and TUKIOSCO_PASSWORD):
        raise RuntimeError("Faltan TUKIOSCO_BASE_URL, TUKIOSCO_EMAIL o TUKIOSCO_PASSWORD.")

    url = f"{TUKIOSCO_BASE_URL}/users/login"       # ver colección
    payload = {"email": TUKIOSCO_EMAIL, "password": TUKIOSCO_PASSWORD}
    try:
        resp = _session().post(url, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        raise RuntimeError(f"Error conectando login TuKiosco: {e}")

    token = data.get("token") or data.get("accessToken") or data.get("jwt")  # por si tu backend nombra distinto
    if not token:
        raise RuntimeError(f"Login TuKiosco inválido: {data}")
    return token

def _ensure_tk_token(force: bool = False, ttl_seconds: Optional[int] = None) -> str:
    """
    Asegura JWT en cache. Si force=True o expiró TTL, relogin.
    """
    global _TK_TOKEN, _TK_TOKEN_TS
    now = time.time()
    if force or (not _TK_TOKEN) or (ttl_seconds and _TK_TOKEN_TS and (now - _TK_TOKEN_TS > ttl_seconds)):
        _TK_TOKEN = _tk_login()
        _TK_TOKEN_TS = now
    return _TK_TOKEN

def _tk_request(
    method: str,
    path: str,
    token: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    timeout: int = 25,
) -> Any:
    """
    Hace la llamada con Authorization: Bearer <token>.
    Devuelve JSON ya parseado o dict de error homogéneo.
    """
    base = TUKIOSCO_BASE_URL.rstrip("/")
    url = f"{base}/{path.lstrip('/')}"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        resp = _session().request(
            method=method.upper(),
            url=url,
            headers=headers,
            params=params,
            json=json_body,
            timeout=timeout
        )
        # 401 puede indicar token inválido/expirado
        if resp.status_code == 401:
            return {"exception": "unauthorized", "status": 401, "message": "Unauthorized"}
        resp.raise_for_status()
        # algunos endpoints devuelven 204 sin body
        return resp.json() if resp.content else {"ok": True}
    except requests.RequestException as e:
        return {"exception": "request_failed", "message": str(e), "status": getattr(e.response, "status_code", None)}

def tk_call(
    method: str,
    path: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    auto_retry_on_401: bool = True,
    token_ttl_seconds: Optional[int] = 60*60,  # 1h (ajustable)
) -> Any:
    """
    Wrapper: asegura token, llama, si 401 relogin + reintenta UNA vez.
    """
    token = _ensure_tk_token(force=False, ttl_seconds=token_ttl_seconds)
    data = _tk_request(method, path, token, params=params, json_body=json_body)

    if isinstance(data, dict) and data.get("exception") == "unauthorized" and auto_retry_on_401:
        token = _ensure_tk_token(force=True)
        data = _tk_request(method, path, token, params=params, json_body=json_body)

    return data

# === Helpers específicos (opcionales) ===

def tk_login_user_info() -> Any:
    # GET /users/login/userInfoByToken
    return tk_call("GET", "/users/login/userInfoByToken")

def tk_products_list() -> Any:
    # GET /products
    return tk_call("GET", "/products")

def tk_product_by_id(product_id: int) -> Any:
    # GET /products/{id}
    return tk_call("GET", f"/products/{product_id}")

def tk_sales_create(payload: Dict[str, Any]) -> Any:
    # POST /sales/createSale
    return tk_call("POST", "/sales/createSale", json_body=payload)

def tk_cashbox_current(store_id: int) -> Any:
    # GET /cashbox/current/{storeId}
    return tk_call("GET", f"/cashbox/current/{store_id}")

def getStoreByName(name: str) -> Any:
    # GET /stores/name/{name}
    return tk_call("GET", f"/stores/name/{name}")

# === Shopping Cart API ====

def tk_shopping_carts_by_store(store_id: int) -> Any:
    """
    GET /shoppingCart/store/{storeId}
    Lista los carritos de una tienda específica.
    """
    return tk_call("GET", f"/shoppingCart/store/{store_id}")


def tk_shopping_cart_create(payload: Dict[str, Any]) -> Any:
    """
    POST /shoppingCart/
    Crea un carrito.
    Ejemplo de payload:
    {
      "store_id": 1,
      "customer_phone": "76742300",
      "customer_name": "Juan Pérez",
      "items": [
        {"product_id": 1, "quantity": 2, "unit_price": 20.00},
        {"product_id": 2, "quantity": 1, "unit_price": 5.00}
      ]
    }
    """
    return tk_call("POST", "/shoppingCart/", json_body=payload)


def tk_shopping_cart_update(cart_id: int, payload: Dict[str, Any]) -> Any:
    """
    PUT /shoppingCart/{id}
    Actualiza un carrito existente.
    """
    return tk_call("PUT", f"/shoppingCart/{cart_id}", json_body=payload)


def tk_shopping_cart_delete(cart_id: int) -> Any:
    """
    DELETE /shoppingCart/{id}
    Elimina un carrito.
    """
    return tk_call("DELETE", f"/shoppingCart/{cart_id}")


def tk_shopping_cart_finalize(cart_id: int, payload: Dict[str, Any]) -> Any:
    """
    POST /shoppingCart/{id}/finalize
    Finaliza la venta de un carrito.
    Ejemplo de payload:
    {
      "userId": 1,
      "paymentMethod": "CASH"
    }
    """
    return tk_call("POST", f"/shoppingCart/{cart_id}/finalize", json_body=payload)