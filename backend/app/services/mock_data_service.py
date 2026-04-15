"""
Servicio central de datos mock para demo sin base de datos.

Este módulo concentra:
- Catálogo (8-12 productos + filtros + detalle)
- Admin productos (listado + CRUD básico en memoria)
- Dashboard y analytics
- IA (health, summary, chat y módulos de business intel)
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
from decimal import Decimal
import math
import threading
from typing import Any

from schemas.product_schema import ProductFilterParams, ProductFilterResponse, ProductFilterStats


_LOCK = threading.Lock()


def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _build_products() -> list[dict[str, Any]]:
    return [
        {
            "id": 101,
            "category_id": 10,
            "category_name": "Electrónica",
            "name": "Auriculares NovaSound X1",
            "slug": "auriculares-novasound-x1",
            "description": "Auriculares bluetooth con cancelación de ruido.",
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=1200",
            "price_min": Decimal("89.90"),
            "price_max": Decimal("129.90"),
            "stock_total": 47,
            "id_marca": 1,
            "nom_marca": "NovaSound",
            "id_proveedor": 1,
            "nom_proveedor": "Tech Supplies SAS",
            "is_active": True,
            "rating": 4.7,
            "review_count": 138,
            "images": [
                {"image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=1200", "is_main": True, "sort_order": 0},
                {"image_url": "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=1200", "is_main": False, "sort_order": 1},
            ],
        },
        {
            "id": 102,
            "category_id": 10,
            "category_name": "Electrónica",
            "name": "Smartwatch Pulse Pro",
            "slug": "smartwatch-pulse-pro",
            "description": "Reloj inteligente con métricas deportivas.",
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=1200",
            "price_min": Decimal("149.00"),
            "price_max": Decimal("199.00"),
            "stock_total": 32,
            "id_marca": 2,
            "nom_marca": "Pulse",
            "id_proveedor": 1,
            "nom_proveedor": "Tech Supplies SAS",
            "is_active": True,
            "rating": 4.6,
            "review_count": 94,
            "images": [
                {"image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=1200", "is_main": True, "sort_order": 0}
            ],
        },
        {
            "id": 103,
            "category_id": 20,
            "category_name": "Hogar",
            "name": "Lámpara Nórdica Alba",
            "slug": "lampara-nordica-alba",
            "description": "Lámpara de mesa minimalista con luz cálida.",
            "image_url": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=1200",
            "price_min": Decimal("39.99"),
            "price_max": Decimal("59.99"),
            "stock_total": 15,
            "id_marca": 3,
            "nom_marca": "CasaZen",
            "id_proveedor": 2,
            "nom_proveedor": "Hogar Andino",
            "is_active": True,
            "rating": 4.5,
            "review_count": 57,
            "images": [
                {"image_url": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=1200", "is_main": True, "sort_order": 0}
            ],
        },
        {
            "id": 104,
            "category_id": 30,
            "category_name": "Deportes",
            "name": "Mancuernas Flex 20kg",
            "slug": "mancuernas-flex-20kg",
            "description": "Set ajustable para entrenamiento en casa.",
            "image_url": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=1200",
            "price_min": Decimal("119.00"),
            "price_max": Decimal("149.00"),
            "stock_total": 8,
            "id_marca": 4,
            "nom_marca": "IronFlex",
            "id_proveedor": 3,
            "nom_proveedor": "Fit Logistics",
            "is_active": True,
            "rating": 4.8,
            "review_count": 121,
            "images": [
                {"image_url": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=1200", "is_main": True, "sort_order": 0}
            ],
        },
        {
            "id": 105,
            "category_id": 40,
            "category_name": "Moda",
            "name": "Chaqueta Urban Wind",
            "slug": "chaqueta-urban-wind",
            "description": "Chaqueta liviana impermeable para ciudad.",
            "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=1200",
            "price_min": Decimal("69.90"),
            "price_max": Decimal("89.90"),
            "stock_total": 26,
            "id_marca": 5,
            "nom_marca": "UrbanWear",
            "id_proveedor": 4,
            "nom_proveedor": "Moda Express",
            "is_active": True,
            "rating": 4.4,
            "review_count": 63,
            "images": [
                {"image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=1200", "is_main": True, "sort_order": 0}
            ],
        },
        {
            "id": 106,
            "category_id": 10,
            "category_name": "Electrónica",
            "name": "Teclado Mecánico Orion",
            "slug": "teclado-mecanico-orion",
            "description": "Teclado RGB switches táctiles.",
            "image_url": "https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?w=1200",
            "price_min": Decimal("99.00"),
            "price_max": Decimal("139.00"),
            "stock_total": 52,
            "id_marca": 6,
            "nom_marca": "OrionTech",
            "id_proveedor": 1,
            "nom_proveedor": "Tech Supplies SAS",
            "is_active": True,
            "rating": 4.7,
            "review_count": 188,
            "images": [
                {"image_url": "https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?w=1200", "is_main": True, "sort_order": 0}
            ],
        },
        {
            "id": 107,
            "category_id": 20,
            "category_name": "Hogar",
            "name": "Silla Ergonómica CloudSeat",
            "slug": "silla-ergonomica-cloudseat",
            "description": "Silla de oficina con soporte lumbar.",
            "image_url": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=1200",
            "price_min": Decimal("259.00"),
            "price_max": Decimal("319.00"),
            "stock_total": 12,
            "id_marca": 7,
            "nom_marca": "CloudSeat",
            "id_proveedor": 2,
            "nom_proveedor": "Hogar Andino",
            "is_active": True,
            "rating": 4.9,
            "review_count": 74,
            "images": [
                {"image_url": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=1200", "is_main": True, "sort_order": 0}
            ],
        },
        {
            "id": 108,
            "category_id": 30,
            "category_name": "Deportes",
            "name": "Tapete Yoga Balance",
            "slug": "tapete-yoga-balance",
            "description": "Tapete antideslizante 6mm.",
            "image_url": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=1200",
            "price_min": Decimal("24.90"),
            "price_max": Decimal("34.90"),
            "stock_total": 39,
            "id_marca": 8,
            "nom_marca": "BalanceFit",
            "id_proveedor": 3,
            "nom_proveedor": "Fit Logistics",
            "is_active": True,
            "rating": 4.3,
            "review_count": 45,
            "images": [
                {"image_url": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=1200", "is_main": True, "sort_order": 0}
            ],
        },
        {
            "id": 109,
            "category_id": 40,
            "category_name": "Moda",
            "name": "Tenis Runner Lite",
            "slug": "tenis-runner-lite",
            "description": "Tenis livianos para running urbano.",
            "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=1200",
            "price_min": Decimal("79.00"),
            "price_max": Decimal("109.00"),
            "stock_total": 33,
            "id_marca": 9,
            "nom_marca": "Runner",
            "id_proveedor": 4,
            "nom_proveedor": "Moda Express",
            "is_active": True,
            "rating": 4.6,
            "review_count": 81,
            "images": [
                {"image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=1200", "is_main": True, "sort_order": 0}
            ],
        },
        {
            "id": 110,
            "category_id": 10,
            "category_name": "Electrónica",
            "name": "Parlante Echo Mini",
            "slug": "parlante-echo-mini",
            "description": "Parlante portátil con batería de 10h.",
            "image_url": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=1200",
            "price_min": Decimal("59.00"),
            "price_max": Decimal("79.00"),
            "stock_total": 0,
            "id_marca": 1,
            "nom_marca": "NovaSound",
            "id_proveedor": 1,
            "nom_proveedor": "Tech Supplies SAS",
            "is_active": False,
            "rating": 4.1,
            "review_count": 29,
            "images": [
                {"image_url": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=1200", "is_main": True, "sort_order": 0}
            ],
        },
    ]


_STATE: dict[str, Any] = {
    "products": _build_products(),
    "categories": [
        {"id": 10, "name": "Electrónica", "slug": "electronica", "parent_id": None, "level": 0},
        {"id": 20, "name": "Hogar", "slug": "hogar", "parent_id": None, "level": 0},
        {"id": 30, "name": "Deportes", "slug": "deportes", "parent_id": None, "level": 0},
        {"id": 40, "name": "Moda", "slug": "moda", "parent_id": None, "level": 0},
    ],
    "brands": [
        {"id_marca": 1, "nom_marca": "NovaSound"},
        {"id_marca": 2, "nom_marca": "Pulse"},
        {"id_marca": 3, "nom_marca": "CasaZen"},
        {"id_marca": 4, "nom_marca": "IronFlex"},
        {"id_marca": 5, "nom_marca": "UrbanWear"},
    ],
    "providers": [
        {"id_proveedor": 1, "nom_proveedor": "Tech Supplies SAS"},
        {"id_proveedor": 2, "nom_proveedor": "Hogar Andino"},
        {"id_proveedor": 3, "nom_proveedor": "Fit Logistics"},
        {"id_proveedor": 4, "nom_proveedor": "Moda Express"},
    ],
    "category_attributes": {},
}


def _product_to_admin_item(p: dict[str, Any], total_registros: int) -> dict[str, Any]:
    return {
        "category_id": str(p["category_id"]),
        "id": str(p["id"]),
        "category_name": p["category_name"],
        "name": p["name"],
        "description": p.get("description"),
        "slug_producto": p.get("slug"),
        "image_url": p.get("image_url"),
        "price_min": str(p["price_min"]),
        "price_max": str(p["price_max"]),
        "stock_total": int(p["stock_total"]),
        "id_marca": str(p["id_marca"]),
        "nom_marca": p["nom_marca"],
        "id_proveedor": str(p["id_proveedor"]) if p.get("id_proveedor") is not None else None,
        "nom_proveedor": p.get("nom_proveedor"),
        "fec_insert": _now_iso(),
        "is_active": bool(p["is_active"]),
        "ind_activo_categoria": True,
        "ind_activo_marca": True,
        "total_registros": total_registros,
    }


def get_products_public() -> list[dict[str, Any]]:
    with _LOCK:
        products = [p for p in _STATE["products"] if p.get("is_active", True)]
    out: list[dict[str, Any]] = []
    for p in products:
        item = {
            "id": Decimal(str(p["id"])),
            "category_id": Decimal(str(p["category_id"])),
            "name": p["name"],
            "slug": p.get("slug"),
            "description": p.get("description"),
            "id_marca": Decimal(str(p["id_marca"])),
            "is_active": True,
            "category_name": p.get("category_name"),
            "price_min": p.get("price_min"),
            "stock_total": int(p.get("stock_total", 0)),
            "image_url": p.get("image_url"),
            "rating": p.get("rating"),
            "review_count": int(p.get("review_count", 0)),
            "images": deepcopy(p.get("images", [])),
            "variants": [
                {
                    "id": f"{p['id']}-v1",
                    "sku": f"MOCK-{p['id']}",
                    "price": float(p["price_min"]),
                    "stock": int(p["stock_total"]),
                    "is_active": bool(p["is_active"]),
                }
            ],
            "variant_groups": [],
            "product_images": deepcopy(p.get("images", [])),
        }
        out.append(item)
    return out


def get_product_by_slug_or_id(slug_or_id: str) -> dict[str, Any] | None:
    raw = str(slug_or_id).strip().lower()
    with _LOCK:
        for p in _STATE["products"]:
            if str(p["id"]) == raw or str(p.get("slug", "")).lower() == raw:
                return {
                    "id": Decimal(str(p["id"])),
                    "category_id": Decimal(str(p["category_id"])),
                    "name": p["name"],
                    "slug": p.get("slug"),
                    "description": p.get("description"),
                    "id_marca": Decimal(str(p["id_marca"])),
                    "is_active": bool(p["is_active"]),
                    "category_name": p.get("category_name"),
                    "price_min": p.get("price_min"),
                    "stock_total": int(p.get("stock_total", 0)),
                    "image_url": p.get("image_url"),
                    "rating": p.get("rating"),
                    "review_count": int(p.get("review_count", 0)),
                    "images": deepcopy(p.get("images", [])),
                    "variants": [
                        {
                            "id": f"{p['id']}-v1",
                            "sku": f"MOCK-{p['id']}",
                            "price": float(p["price_min"]),
                            "stock": int(p["stock_total"]),
                            "is_active": bool(p["is_active"]),
                        }
                    ],
                    "images_by_variant": {f"{p['id']}-v1": deepcopy(p.get("images", []))},
                    "variant_groups": [],
                    "product_images": deepcopy(p.get("images", [])),
                }
    return None


def get_products_admin(params: dict[str, Any] | None) -> list[dict[str, Any]]:
    params = params or {}
    with _LOCK:
        items = deepcopy(_STATE["products"])
    search = (params.get("search") or "").strip().lower()
    category_id = params.get("category_id")
    id_marca = params.get("id_marca")
    id_proveedor = params.get("id_proveedor")
    if search:
        items = [p for p in items if search in p["name"].lower()]
    if category_id:
        items = [p for p in items if int(p["category_id"]) == int(category_id)]
    if id_marca:
        items = [p for p in items if int(p["id_marca"]) == int(id_marca)]
    if id_proveedor:
        items = [p for p in items if int(p["id_proveedor"]) == int(id_proveedor)]

    total = len(items)
    order_by = params.get("ordenar_por", "nombre")
    reverse = str(params.get("orden", "ASC")).upper() == "DESC"
    if order_by == "precio":
        items.sort(key=lambda x: float(x["price_min"]), reverse=reverse)
    elif order_by == "stock":
        items.sort(key=lambda x: int(x["stock_total"]), reverse=reverse)
    elif order_by == "categoria":
        items.sort(key=lambda x: x["category_name"], reverse=reverse)
    elif order_by == "marca":
        items.sort(key=lambda x: x["nom_marca"], reverse=reverse)
    else:
        items.sort(key=lambda x: x["name"], reverse=reverse)

    limit = int(params.get("limit", 50))
    offset = int(params.get("offset", 0))
    paged = items[offset : offset + limit]
    out = [_product_to_admin_item(p, total) for p in paged]
    if out:
        stock_en = sum(1 for p in items if int(p["stock_total"]) > 10 and p["is_active"])
        stock_bajo = sum(1 for p in items if 0 < int(p["stock_total"]) <= 10 and p["is_active"])
        stock_sin = sum(1 for p in items if int(p["stock_total"]) == 0 and p["is_active"])
        out[0]["stock_stats_en_stock"] = stock_en
        out[0]["stock_stats_bajo"] = stock_bajo
        out[0]["stock_stats_sin_stock"] = stock_sin
    return out


def toggle_product(product_id: int, active: bool) -> None:
    with _LOCK:
        for p in _STATE["products"]:
            if int(p["id"]) == int(product_id):
                p["is_active"] = bool(active)
                return
    raise ValueError("Producto no encontrado")


def update_product_composite(product_id: int, payload: Any) -> None:
    with _LOCK:
        for p in _STATE["products"]:
            if int(p["id"]) != int(product_id):
                continue
            p["name"] = payload.product.name
            p["description"] = payload.product.description
            p["category_id"] = int(payload.product.category_id)
            p["id_marca"] = int(payload.product.id_marca) if payload.product.id_marca is not None else p["id_marca"]
            p["id_proveedor"] = int(payload.product.id_proveedor) if payload.product.id_proveedor is not None else p["id_proveedor"]
            p["is_active"] = bool(payload.product.is_active)
            if payload.variants:
                prices = [Decimal(str(v.price)) for v in payload.variants]
                stocks = [int(v.stock) for v in payload.variants]
                p["price_min"] = min(prices)
                p["price_max"] = max(prices)
                p["stock_total"] = sum(stocks)
            if payload.image_urls:
                p["image_url"] = payload.image_urls[0]
                p["images"] = [{"image_url": u, "is_main": idx == 0, "sort_order": idx} for idx, u in enumerate(payload.image_urls)]
            return
    raise ValueError("Producto no encontrado")


def create_product_composite(payload: Any) -> int:
    with _LOCK:
        next_id = max(int(p["id"]) for p in _STATE["products"]) + 1
        category_map = {int(c["id"]): c["name"] for c in _STATE["categories"]}
        brand_map = {int(b["id_marca"]): b["nom_marca"] for b in _STATE["brands"]}
        provider_map = {int(p["id_proveedor"]): p["nom_proveedor"] for p in _STATE["providers"]}
        prices = [Decimal(str(v.price)) for v in payload.variants] or [Decimal("0")]
        stocks = [int(v.stock) for v in payload.variants] or [0]
        image_urls = payload.image_urls or []
        item = {
            "id": next_id,
            "category_id": int(payload.product.category_id),
            "category_name": category_map.get(int(payload.product.category_id), "General"),
            "name": payload.product.name,
            "slug": payload.product.name.lower().replace(" ", "-"),
            "description": payload.product.description,
            "image_url": image_urls[0] if image_urls else None,
            "price_min": min(prices),
            "price_max": max(prices),
            "stock_total": sum(stocks),
            "id_marca": int(payload.product.id_marca or 1),
            "nom_marca": brand_map.get(int(payload.product.id_marca or 1), "Marca Demo"),
            "id_proveedor": int(payload.product.id_proveedor or 1),
            "nom_proveedor": provider_map.get(int(payload.product.id_proveedor or 1), "Proveedor Demo"),
            "is_active": bool(payload.product.is_active),
            "rating": 4.5,
            "review_count": 0,
            "images": [{"image_url": u, "is_main": i == 0, "sort_order": i} for i, u in enumerate(image_urls)],
        }
        _STATE["products"].append(item)
        return next_id


def get_filter_options(category_id: int | None = None) -> dict[str, Any]:
    with _LOCK:
        categories = deepcopy(_STATE["categories"])
        brands = deepcopy(_STATE["brands"])
        products = deepcopy(_STATE["products"])
    active_products = [p for p in products if p.get("is_active", True)]
    if category_id is not None:
        active_products = [p for p in active_products if int(p["category_id"]) == int(category_id)]
    prices = [float(p["price_min"]) for p in active_products] or [0]
    return {
        "categorias": categories,
        "marcas": brands,
        "precio_rango": {"minimo": min(prices), "maximo": max(prices)},
        "attributes": [],
    }


def get_filter_options_admin() -> dict[str, Any]:
    options = get_filter_options()
    with _LOCK:
        providers = deepcopy(_STATE["providers"])
    return {
        "categorias": options["categorias"],
        "marcas": options["marcas"],
        "proveedores": providers,
        "precio_rango": options["precio_rango"],
    }


def _next_id(key: str, id_field: str) -> int:
    rows = _STATE.get(key, [])
    if not rows:
        return 1
    return max(int(r.get(id_field, 0)) for r in rows) + 1


def get_providers() -> list[dict[str, Any]]:
    with _LOCK:
        providers = deepcopy(_STATE["providers"])
    out = []
    for p in providers:
        out.append(
            {
                "id_proveedor": Decimal(str(p["id_proveedor"])),
                "nom_proveedor": p["nom_proveedor"],
                "email": p.get("email", f"contacto{p['id_proveedor']}@mock.local"),
                "tel_proveedor": Decimal(str(p.get("tel_proveedor", 3000000000 + p["id_proveedor"]))),
                "ind_activo": bool(p.get("ind_activo", True)),
                "usr_insert": Decimal("1"),
                "fec_insert": datetime.utcnow(),
                "usr_update": None,
                "fec_update": None,
            }
        )
    return out


def get_provider_by_id(provider_id: int) -> dict[str, Any] | None:
    rows = get_providers()
    for row in rows:
        if int(row["id_proveedor"]) == int(provider_id):
            return row
    return None


def create_provider(payload: dict[str, Any]) -> str:
    with _LOCK:
        pid = _next_id("providers", "id_proveedor")
        _STATE["providers"].append(
            {
                "id_proveedor": pid,
                "nom_proveedor": payload.get("nom_proveedor", f"Proveedor {pid}"),
                "email": payload.get("email"),
                "tel_proveedor": payload.get("tel_proveedor"),
                "ind_activo": payload.get("ind_activo", True),
            }
        )
    return f"OK:{pid}"


def update_provider(provider_id: int, payload: dict[str, Any]) -> str:
    with _LOCK:
        for p in _STATE["providers"]:
            if int(p["id_proveedor"]) != int(provider_id):
                continue
            p.update({k: v for k, v in payload.items() if v is not None})
            return "OK"
    raise ValueError("Proveedor no encontrado")


def toggle_provider(provider_id: int, active: bool) -> str:
    with _LOCK:
        for p in _STATE["providers"]:
            if int(p["id_proveedor"]) == int(provider_id):
                p["ind_activo"] = bool(active)
                return "OK"
    raise ValueError("Proveedor no encontrado")


def get_brands() -> list[dict[str, Any]]:
    with _LOCK:
        brands = deepcopy(_STATE["brands"])
    out = []
    for b in brands:
        out.append(
            {
                "id_marca": Decimal(str(b["id_marca"])),
                "nom_marca": b["nom_marca"],
                "ind_activo": bool(b.get("ind_activo", True)),
                "usr_insert": Decimal("1"),
                "fec_insert": datetime.utcnow(),
                "usr_update": None,
                "fec_update": None,
            }
        )
    return out


def create_brand(payload: dict[str, Any]) -> str:
    with _LOCK:
        bid = _next_id("brands", "id_marca")
        _STATE["brands"].append(
            {
                "id_marca": bid,
                "nom_marca": payload.get("nom_marca", f"Marca {bid}"),
                "ind_activo": payload.get("ind_activo", True),
            }
        )
    return "OK"


def update_brand(brand_id: int, payload: dict[str, Any]) -> str:
    with _LOCK:
        for b in _STATE["brands"]:
            if int(b["id_marca"]) != int(brand_id):
                continue
            b.update({k: v for k, v in payload.items() if v is not None})
            return "OK"
    raise ValueError("Marca no encontrada")


def toggle_brand(brand_id: int, active: bool) -> str:
    with _LOCK:
        for b in _STATE["brands"]:
            if int(b["id_marca"]) == int(brand_id):
                b["ind_activo"] = bool(active)
                return "OK"
    raise ValueError("Marca no encontrada")


def get_categories() -> list[dict[str, Any]]:
    with _LOCK:
        categories = deepcopy(_STATE["categories"])
    out = []
    for c in categories:
        cid = int(c["id"])
        products_count = sum(1 for p in _STATE["products"] if int(p["category_id"]) == cid and bool(p.get("is_active", True)))
        out.append(
            {
                "id": Decimal(str(cid)),
                "name": c["name"],
                "slug": c.get("slug"),
                "parent_id": Decimal(str(c["parent_id"])) if c.get("parent_id") is not None else None,
                "is_active": bool(c.get("is_active", True)),
                "ind_activo": bool(c.get("is_active", True)),
                "usr_insert": Decimal("1"),
                "fec_insert": datetime.utcnow(),
                "usr_update": None,
                "fec_update": None,
                "productos_count": products_count,
            }
        )
    return out


def get_category_by_id(category_id: int) -> dict[str, Any] | None:
    for c in get_categories():
        if int(c["id"]) == int(category_id):
            return c
    return None


def create_category(payload: dict[str, Any]) -> int:
    with _LOCK:
        cid = _next_id("categories", "id")
        name = payload.get("name", f"Categoría {cid}")
        _STATE["categories"].append(
            {
                "id": cid,
                "name": name,
                "slug": str(name).strip().lower().replace(" ", "-"),
                "parent_id": int(payload["parent_id"]) if payload.get("parent_id") is not None else None,
                "is_active": payload.get("is_active", payload.get("ind_activo", True)),
                "level": 0,
            }
        )
        _STATE["category_attributes"][cid] = []
    return cid


def update_category(category_id: int, payload: dict[str, Any]) -> str:
    with _LOCK:
        for c in _STATE["categories"]:
            if int(c["id"]) != int(category_id):
                continue
            if payload.get("name") is not None:
                c["name"] = payload["name"]
                c["slug"] = str(payload["name"]).strip().lower().replace(" ", "-")
            if payload.get("parent_id") is not None:
                c["parent_id"] = int(payload["parent_id"])
            is_active = payload.get("is_active", payload.get("ind_activo"))
            if is_active is not None:
                c["is_active"] = bool(is_active)
            return "OK"
    raise ValueError("Categoría no encontrada")


def toggle_category(category_id: int, active: bool) -> str:
    with _LOCK:
        for c in _STATE["categories"]:
            if int(c["id"]) == int(category_id):
                c["is_active"] = bool(active)
                return "OK"
    raise ValueError("Categoría no encontrada")


def get_category_attributes(category_id: int) -> list[dict[str, Any]]:
    with _LOCK:
        items = deepcopy(_STATE["category_attributes"].get(int(category_id), []))
    out = []
    for idx, it in enumerate(items, start=1):
        out.append(
            {
                "id": Decimal(str(idx)),
                "category_id": Decimal(str(category_id)),
                "attribute_id": Decimal(str(it["attribute_id"])),
                "is_required": bool(it.get("is_required", False)),
                "is_filterable": bool(it.get("is_filterable", False)),
                "attribute_name": f"Atributo {it['attribute_id']}",
                "data_type": "text",
                "has_predefined_values": False,
            }
        )
    return out


def set_category_attributes(category_id: int, items: list[dict[str, Any]]) -> None:
    normalized = []
    for it in items:
        normalized.append(
            {
                "attribute_id": int(it["attribute_id"]),
                "is_required": bool(it.get("is_required", False)),
                "is_filterable": bool(it.get("is_filterable", False)),
            }
        )
    with _LOCK:
        _STATE["category_attributes"][int(category_id)] = normalized


def get_product_admin_detail(product_id: int) -> dict[str, Any] | None:
    with _LOCK:
        product = next((p for p in _STATE["products"] if int(p["id"]) == int(product_id)), None)
    if not product:
        return None
    return {
        "product": {
            "name": product["name"],
            "category_id": int(product["category_id"]),
            "id_marca": int(product["id_marca"]),
            "id_proveedor": int(product["id_proveedor"]),
            "description": product.get("description"),
            "is_active": bool(product.get("is_active", True)),
        },
        "variants": [
            {
                "id": int(product["id"]) * 10 + 1,
                "group_id": int(product["id"]),
                "sku": f"MOCK-{product['id']}",
                "price": float(product["price_min"]),
                "stock": int(product["stock_total"]),
                "is_active": bool(product.get("is_active", True)),
                "attributes": {},
                "tipo_clasificacion": "Estándar",
            }
        ],
        "image_urls": [img["image_url"] for img in product.get("images", []) if img.get("image_url")],
        "images_by_variant": {
            str(int(product["id"]) * 10 + 1): deepcopy(product.get("images", []))
        },
        "variant_groups": [],
    }


def filter_products(filters: ProductFilterParams) -> ProductFilterResponse:
    with _LOCK:
        products = deepcopy(_STATE["products"])
    items = [p for p in products if p.get("is_active", True)]
    if filters.category_id is not None:
        items = [p for p in items if int(p["category_id"]) == int(filters.category_id)]
    if filters.id_marca is not None:
        items = [p for p in items if int(p["id_marca"]) == int(filters.id_marca)]
    if filters.nombre_producto:
        q = filters.nombre_producto.strip().lower()
        items = [p for p in items if q in p["name"].lower()]
    if filters.precio_min is not None:
        items = [p for p in items if Decimal(str(p["price_min"])) >= filters.precio_min]
    if filters.precio_max is not None:
        items = [p for p in items if Decimal(str(p["price_min"])) <= filters.precio_max]
    if filters.solo_con_stock:
        items = [p for p in items if int(p["stock_total"]) > 0]

    reverse = filters.orden.upper() == "DESC"
    if filters.ordenar_por == "precio":
        items.sort(key=lambda x: float(x["price_min"]), reverse=reverse)
    elif filters.ordenar_por == "stock":
        items.sort(key=lambda x: int(x["stock_total"]), reverse=reverse)
    elif filters.ordenar_por == "fecha":
        items.sort(key=lambda x: int(x["id"]), reverse=reverse)
    else:
        items.sort(key=lambda x: x["name"], reverse=reverse)

    total = len(items)
    paged = items[filters.offset : filters.offset + filters.limit]
    response_products = []
    for p in paged:
        response_products.append(
            {
                "category_id": int(p["category_id"]),
                "id": int(p["id"]),
                "slug": p.get("slug"),
                "category_name": p["category_name"],
                "name": p["name"],
                "description": p.get("description"),
                "image_url": p.get("image_url"),
                "price_min": Decimal(str(p["price_min"])),
                "price_max": Decimal(str(p["price_max"])),
                "stock_total": int(p["stock_total"]),
                "total_registros": total,
                "rating": p.get("rating"),
                "id_marca": int(p["id_marca"]),
                "nom_marca": p["nom_marca"],
                "fec_insert": None,
            }
        )

    total_pages = math.ceil(total / filters.limit) if filters.limit else 1
    page = (filters.offset // filters.limit) + 1 if filters.limit else 1
    return ProductFilterResponse(
        products=response_products,
        total=total,
        page=page,
        total_pages=total_pages,
        limit=filters.limit,
        offset=filters.offset,
    )


def get_filter_stats(filters: ProductFilterParams) -> ProductFilterStats:
    filtered = filter_products(
        ProductFilterParams(
            **{**filters.model_dump(), "limit": 10000, "offset": 0}
        )
    )
    rows = filtered.products
    if not rows:
        return ProductFilterStats(
            total_productos=0,
            precio_minimo=None,
            precio_maximo=None,
            precio_promedio=None,
            total_stock=0,
            categorias_disponibles=0,
            marcas_disponibles=0,
        )
    prices = [Decimal(str(p.price_min)) for p in rows]
    return ProductFilterStats(
        total_productos=len(rows),
        precio_minimo=min(prices),
        precio_maximo=max(prices),
        precio_promedio=sum(prices) / Decimal(len(prices)),
        total_stock=sum(int(p.stock_total) for p in rows),
        categorias_disponibles=len(set(int(p.category_id) for p in rows)),
        marcas_disponibles=len(set(int(p.id_marca or 0) for p in rows)),
    )


def get_dashboard_data(time_range: str = "monthly") -> dict[str, Any]:
    return {
        "kpis": {
            "totalOrders": {"value": 428, "growth": 12.4, "trend": "up", "formatted": "428"},
            "unitsSold": {"value": 963, "growth": 9.8, "trend": "up", "formatted": "963"},
            "shippedOrders": {"value": 389, "growth": 8.1, "trend": "up", "formatted": "389"},
            "totalRevenue": {"value": 248930.0, "growth": 15.2, "trend": "up", "formatted": "$248.930"},
        },
        "salesData": [
            {"period": "2026-01", "sales": 61200.0, "orders": 104},
            {"period": "2026-02", "sales": 67450.0, "orders": 112},
            {"period": "2026-03", "sales": 70180.0, "orders": 118},
            {"period": "2026-04", "sales": 50000.0, "orders": 94},
        ],
        "bestSellers": [
            {"id": "106", "name": "Teclado Mecánico Orion", "image": "https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?w=1200", "sales": 216, "revenue": 21400.0},
            {"id": "101", "name": "Auriculares NovaSound X1", "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=1200", "sales": 192, "revenue": 17100.0},
            {"id": "109", "name": "Tenis Runner Lite", "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=1200", "sales": 140, "revenue": 11800.0},
        ],
        "recentOrders": [
            {"id": "9801", "customer": "Laura Gómez", "date": _now_iso(), "amount": 289.0, "status": "pending", "items": 3},
            {"id": "9800", "customer": "Julián Pérez", "date": (datetime.utcnow() - timedelta(hours=2)).isoformat() + "Z", "amount": 149.0, "status": "delivered", "items": 1},
            {"id": "9799", "customer": "Camila Rojas", "date": (datetime.utcnow() - timedelta(hours=4)).isoformat() + "Z", "amount": 89.9, "status": "delivered", "items": 1},
        ],
        "summary": {"totalSales": 248930.0, "totalOrders": 428, "conversionRate": "3.8"},
        "timeRange": time_range,
    }


def get_analytics_data() -> dict[str, Any]:
    return {
        "conversionMetrics": [
            {"title": "Tasa de Conversión", "value": "3.8%", "change": "0.6%", "icon": "IconTarget"},
            {"title": "Valor Promedio de Orden", "value": "$582.000", "change": "4.2%", "icon": "IconShoppingCart"},
            {"title": "Total de Órdenes", "value": "428", "change": "12.4%", "icon": "IconPackage"},
            {"title": "Ingresos Totales", "value": "$248.930.000", "change": "15.2%", "icon": "IconCash"},
        ],
        "trafficSources": [
            {"source": "Direct", "visitors": 214, "percentage": 50.0, "change": 8.1},
            {"source": "Google Organic", "visitors": 150, "percentage": 35.0, "change": 11.2},
            {"source": "Social Media", "visitors": 64, "percentage": 15.0, "change": 6.3},
        ],
        "customerDemographics": [
            {"ageGroup": "18-24", "percentage": 18.4, "revenue": 45800.0},
            {"ageGroup": "25-34", "percentage": 37.5, "revenue": 93200.0},
            {"ageGroup": "35-44", "percentage": 24.2, "revenue": 60300.0},
            {"ageGroup": "45-54", "percentage": 14.8, "revenue": 36700.0},
            {"ageGroup": "55+", "percentage": 5.1, "revenue": 12930.0},
        ],
        "productPerformance": [
            {"category": "Electrónica", "sales": 114000.0, "growth": 16.1, "percentage": 45.8},
            {"category": "Moda", "sales": 58200.0, "growth": 11.3, "percentage": 23.4},
            {"category": "Hogar", "sales": 43600.0, "growth": 8.9, "percentage": 17.5},
            {"category": "Deportes", "sales": 33130.0, "growth": 7.2, "percentage": 13.3},
        ],
        "geoData": [
            {"region": "Bogotá", "orders": 137, "revenue": 84500.0},
            {"region": "Medellín", "orders": 96, "revenue": 59200.0},
            {"region": "Cali", "orders": 71, "revenue": 40100.0},
            {"region": "Barranquilla", "orders": 54, "revenue": 31000.0},
        ],
        "hourlyTraffic": [{"hour": str(h).zfill(2), "visitors": (12 + h * 2) if 8 <= h <= 20 else 4} for h in range(24)],
        "productMetrics": {
            "productosActivos": 9,
            "productosInactivos": 1,
            "sinStock": 1,
            "precioPromedio": 98.77,
            "ratingPromedio": 4.56,
            "categoriasActivas": 4,
            "variantesActivas": 10,
        },
    }


def ai_health() -> dict[str, Any]:
    return {"enabled": True, "model": "mock-ai-v1"}


def ai_summary(time_range: str = "monthly") -> dict[str, Any]:
    dash = get_dashboard_data(time_range)
    k = dash["kpis"]
    text = (
        f"En {time_range}, la tienda registra {k['totalOrders']['formatted']} órdenes y "
        f"{k['unitsSold']['formatted']} unidades vendidas. "
        f"Los ingresos van en {k['totalRevenue']['formatted']} con tendencia positiva. "
        "El foco recomendado es reabastecer productos con bajo stock y empujar campañas en electrónica."
    )
    return {"summary": text}


def ai_chat_reply(message: str) -> dict[str, Any]:
    msg = (message or "").lower()
    if "resumen" in msg or "estado" in msg:
        return {"reply": ai_summary()["summary"]}
    if "stock" in msg:
        return {
            "reply": "Hay 1 producto sin stock y 2 en stock bajo. Recomendación: priorizar reposición de 'Mancuernas Flex 20kg' y 'Lámpara Nórdica Alba'."
        }
    if "categoria" in msg:
        return {"reply": "La categoría líder es Electrónica (45.8% de ingresos), seguida de Moda (23.4%)."}
    return {
        "reply": "Modo mock activo: puedo responder sobre ventas, productos, stock, categorías y recomendaciones operativas."
    }


def ai_stream_text(message: str) -> str:
    return ai_chat_reply(message)["reply"]


def ai_business_payload(kind: str) -> dict[str, Any]:
    base = {
        "summary": "",
        "data": {},
        "recommendations": [],
        "generated_at": _now_iso(),
    }
    if kind == "demand":
        base["summary"] = "La demanda proyectada crece en electrónica y moda para las próximas 4 semanas."
        base["data"] = {"top_products": ["Teclado Mecánico Orion", "Auriculares NovaSound X1"], "expected_growth_pct": 12.3}
        base["recommendations"] = ["Aumentar inventario 15% en top productos", "Mantener campañas de retargeting"]
        return base
    if kind == "production":
        base["summary"] = "Se recomienda incrementar producción/reposición en SKUs de rotación alta."
        base["data"] = {"safety_factor": 1.15, "priority_skus": ["MOCK-106", "MOCK-101", "MOCK-109"]}
        base["recommendations"] = ["Ejecutar compra semanal para SKUs prioritarios", "Revisar lead times de proveedor Tech Supplies SAS"]
        return base
    if kind == "anomalies":
        base["summary"] = "Se detectan anomalías leves en caída de tráfico nocturno y picos de cancelación."
        base["data"] = {"anomalies": [{"type": "cancel_rate", "severity": "medium"}, {"type": "night_traffic", "severity": "low"}]}
        base["recommendations"] = ["Auditar método de pago principal", "Optimizar pauta en franjas 18:00-22:00"]
        return base
    if kind == "export":
        base["summary"] = "La tienda está lista para expansión regional con ajustes menores de catálogo."
        base["data"] = {"readiness_score": 81, "gaps": ["fichas técnicas incompletas en 2 productos"]}
        base["recommendations"] = ["Completar atributos faltantes", "Definir estrategia de envíos para región Caribe"]
        return base
    base["summary"] = "La operación muestra salud positiva con margen de mejora en inventario y conversión."
    base["data"] = {"health_score": 84, "focus_areas": ["conversion", "inventory_turnover"]}
    base["recommendations"] = ["Lanzar bundle en top categorías", "Activar alerta automática de stock bajo"]
    return base
