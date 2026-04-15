"""
Inteligencia de negocio heurística para el asistente admin (PyMEs).

Sin modelos ML externos: promedios móviles, comparación ventana reciente vs anterior,
y reglas simples de severidad. Reutiliza el mismo criterio de "venta completada" que
el dashboard: tab_ordenes.ind_estado = 2.

Las funciones devuelven dicts listos para JSON (summary, data, recommendations, generated_at).
El chat convierte el mismo dict a markdown legible vía format_business_payload_markdown().
"""
from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

# Órdenes contadas como venta efectiva (alineado con dashboard_service._get_best_sellers)
ORDER_COMPLETED_STATUS = 2


def _iso_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _f(x: Any) -> float:
    if x is None:
        return 0.0
    if isinstance(x, Decimal):
        return float(x)
    return float(x or 0)


def _i(x: Any) -> int:
    if x is None:
        return 0
    return int(x or 0)


def _window_bounds(days: int) -> tuple[datetime, datetime, datetime, datetime]:
    """recent [recent_start, end], previous [prev_start, prev_end) mismo largo."""
    end = datetime.now()
    recent_start = end - timedelta(days=max(1, days))
    prev_end = recent_start
    prev_start = prev_end - timedelta(days=max(1, days))
    return recent_start, end, prev_start, prev_end


def _product_units_in_range(
    db: Session,
    start: datetime,
    end: datetime,
    product_id: Optional[int] = None,
    category_id: Optional[int] = None,
) -> list[dict[str, Any]]:
    """Unidades vendidas por producto en rango (órdenes completadas)."""
    q = text("""
        SELECT
            p.id AS product_id,
            p.name AS product_name,
            COALESCE(SUM(op.cant_producto), 0)::BIGINT AS units
        FROM tab_products p
        LEFT JOIN tab_product_variant_groups g ON g.product_id = p.id
        LEFT JOIN tab_product_variant_combinations pv ON pv.group_id = g.id AND pv.is_active = TRUE
        LEFT JOIN tab_orden_productos op ON op.variant_id = pv.id
        LEFT JOIN tab_ordenes o ON op.id_orden = o.id_orden
            AND o.ind_estado = :completed
            AND o.fec_pedido >= :start_ts
            AND o.fec_pedido <= :end_ts
        WHERE p.is_active = TRUE
          AND (:pid IS NULL OR p.id = :pid)
          AND (:cid IS NULL OR p.category_id = :cid)
        GROUP BY p.id, p.name
        HAVING COALESCE(SUM(op.cant_producto), 0) > 0
        ORDER BY units DESC
    """)
    rows = db.execute(
        q,
        {
            "completed": ORDER_COMPLETED_STATUS,
            "start_ts": start,
            "end_ts": end,
            "pid": product_id,
            "cid": category_id,
        },
    ).mappings().all()
    return [dict(r) for r in rows]


def _product_stock_rows(db: Session, limit: int = 200) -> list[dict[str, Any]]:
    q = text("""
        WITH product_stock AS (
            SELECT p.id, p.name, p.category_id,
                COALESCE(SUM(c.stock), 0)::BIGINT AS stock_total
            FROM tab_products p
            LEFT JOIN tab_product_variant_groups g ON g.product_id = p.id
            LEFT JOIN tab_product_variant_combinations c ON c.group_id = g.id AND c.is_active = TRUE
            WHERE p.is_active = TRUE
            GROUP BY p.id, p.name, p.category_id
        )
        SELECT id AS product_id, name AS product_name, category_id, stock_total
        FROM product_stock
        ORDER BY id
        LIMIT :lim
    """)
    return [dict(r) for r in db.execute(q, {"lim": limit}).mappings().all()]


def _store_revenue_completed(db: Session, start: datetime, end: datetime) -> float:
    q = text("""
        SELECT COALESCE(SUM(val_total_pedido), 0) AS rev
        FROM tab_ordenes
        WHERE ind_estado = :completed
          AND fec_pedido >= :start_ts
          AND fec_pedido <= :end_ts
    """)
    row = db.execute(
        q,
        {"completed": ORDER_COMPLETED_STATUS, "start_ts": start, "end_ts": end},
    ).mappings().first()
    return _f(row.get("rev") if row else 0)


def _trend_label(recent: float, prev: float) -> str:
    if prev <= 0 and recent > 0:
        return "increasing"
    if prev <= 0:
        return "stable"
    ratio = recent / prev
    if ratio >= 1.15:
        return "increasing"
    if ratio <= 0.85:
        return "decreasing"
    return "stable"


def _confidence_from_units(units: float) -> str:
    if units >= 60:
        return "high"
    if units >= 15:
        return "medium"
    return "low"


def format_business_payload_markdown(payload: dict[str, Any]) -> str:
    """Convierte payload estructurado a markdown accionable para el chat."""
    lines = []
    summary = payload.get("summary") or ""
    if summary:
        lines.append(f"**Resumen:** {summary}")
    data = payload.get("data")
    if data:
        lines.append("\n**Datos clave:**")
        lines.append(f"```json\n{_json_pretty(data)}\n```")
    recs = payload.get("recommendations") or []
    if recs:
        lines.append("\n**Recomendaciones:**")
        for i, r in enumerate(recs, 1):
            lines.append(f"{i}. {r}")
    gen = payload.get("generated_at", "")
    if gen:
        lines.append(f"\n_Generado: {gen}_")
    return "\n".join(lines).strip()


def _json_pretty(obj: Any) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False, indent=2, default=str)


def build_demand_prediction(
    db: Session,
    product_id: Optional[int] = None,
    category_id: Optional[int] = None,
    time_range: int = 30,
) -> dict[str, Any]:
    """
    Predicción heurística de demanda (unidades / período siguiente ≈ ritmo reciente).

    - Compara ventana reciente vs anterior de igual duración.
    - predicted_demand = max(0, round(daily_recent * time_range))
    """
    days = max(7, min(int(time_range), 365))
    rs, re, ps, pe = _window_bounds(days)

    try:
        recent_rows = _product_units_in_range(db, rs, re, product_id, category_id)
        prev_rows = _product_units_in_range(db, ps, pe, product_id, category_id)

        def total_units(rows: list[dict]) -> float:
            return float(sum(_i(r.get("units")) for r in rows))

        if product_id is not None:
            ru = total_units(recent_rows)
            pu = total_units(prev_rows)
            if not recent_rows and ru == 0 and pu == 0:
                row_nm = db.execute(
                    text("SELECT name FROM tab_products WHERE id = :pid LIMIT 1"),
                    {"pid": product_id},
                ).mappings().first()
                pname = row_nm.get("name") if row_nm else "Producto"
                return {
                    "summary": f"No hay ventas completadas recientes para «{pname}» en las ventanas analizadas.",
                    "data": {
                        "scope": "product",
                        "product_id": product_id,
                        "product_name": pname,
                        "window_days": days,
                        "units_recent_window": 0,
                        "units_previous_window": 0,
                        "predicted_units_next_window": 0,
                        "trend": "stable",
                        "confidence": "low",
                    },
                    "recommendations": [
                        "Amplía el rango de días o confirma que el producto tenga ventas en estado completado (2).",
                    ],
                    "generated_at": _iso_now(),
                }
            daily_r = ru / days
            predicted = max(0, round(daily_r * days))
            trend = _trend_label(ru, pu)
            conf = _confidence_from_units(ru + pu)
            name = recent_rows[0]["product_name"] if recent_rows else "Producto"
            data = {
                "scope": "product",
                "product_id": product_id,
                "product_name": name,
                "window_days": days,
                "units_recent_window": int(ru),
                "units_previous_window": int(pu),
                "daily_units_recent": round(daily_r, 2),
                "predicted_units_next_window": predicted,
                "trend": trend,
                "confidence": conf,
                "method": "moving_average_same_length_windows",
            }
            summary = (
                f"Demanda estimada próximos {days} días: ~{predicted} uds "
                f"(tendencia {trend}, confianza {conf})."
            )
            recs = [
                f"Ajusta compras/producción si el stock actual no cubre ~{predicted} uds en {days} días.",
                "Si la confianza es baja, amplía el historial o revisa estacionalidad.",
            ]
            return {
                "summary": summary,
                "data": data,
                "recommendations": recs,
                "generated_at": _iso_now(),
            }

        if category_id is not None:
            ru = total_units(recent_rows)
            pu = total_units(prev_rows)
            daily_r = ru / days
            predicted = max(0, round(daily_r * days))
            trend = _trend_label(ru, pu)
            conf = _confidence_from_units(ru + pu)
            data = {
                "scope": "category",
                "category_id": category_id,
                "window_days": days,
                "units_recent_window": int(ru),
                "units_previous_window": int(pu),
                "predicted_units_next_window": predicted,
                "trend": trend,
                "confidence": conf,
                "method": "moving_average_same_length_windows",
            }
            summary = (
                f"Categoría {category_id}: demanda agregada estimada ~{predicted} uds "
                f"en los próximos {days} días (tendencia {trend})."
            )
            recs = [
                "Prioriza reposición en los SKUs que concentran esas unidades dentro de la categoría.",
                "Revisa productos con stock bajo en esa categoría en Inventario.",
            ]
            return {
                "summary": summary,
                "data": data,
                "recommendations": recs,
                "generated_at": _iso_now(),
            }

        # Tienda: top 5 productos por unidades recientes + forecast
        top = recent_rows[:5]
        items = []
        for r in top:
            pid = _i(r.get("product_id"))
            ru = _i(r.get("units"))
            prev_match = next(
                (x for x in prev_rows if _i(x.get("product_id")) == pid),
                None,
            )
            pu = _i(prev_match.get("units")) if prev_match else 0
            daily_r = ru / days
            pred = max(0, round(daily_r * days))
            items.append(
                {
                    "product_id": pid,
                    "product_name": r.get("product_name"),
                    "units_recent": ru,
                    "units_previous": pu,
                    "predicted_units_next_window": pred,
                    "trend": _trend_label(float(ru), float(pu)),
                    "confidence": _confidence_from_units(float(ru + pu)),
                }
            )
        data = {"scope": "store_top_products", "window_days": days, "items": items}
        summary = (
            f"Top {len(items)} productos por unidades vendidas (últimos {days} días): "
            "ver predicción por ítem en datos."
        )
        recs = [
            "Enfoca producción/compras en el top 3 si el margen y rotación lo sostienen.",
            "Para el resto del catálogo, solicita predicción por producto o categoría.",
        ]
        return {
            "summary": summary,
            "data": data,
            "recommendations": recs,
            "generated_at": _iso_now(),
        }
    except Exception as exc:
        return {
            "summary": "No se pudo calcular la predicción de demanda con los datos actuales.",
            "data": {"error": str(exc)},
            "recommendations": ["Verifica que existan ventas completadas (estado 2) en el rango."],
            "generated_at": _iso_now(),
        }


def build_production_recommendations(
    db: Session,
    time_range: int = 30,
    safety_factor: float = 1.15,
) -> dict[str, Any]:
    """
    Cruza stock actual con demanda reciente por producto.
    suggested_quantity = max(0, ceil(predicted_demand * safety - stock))
    """
    days = max(7, min(int(time_range), 365))
    sf = max(1.0, min(float(safety_factor), 2.0))
    rs, re, _, _ = _window_bounds(days)

    try:
        stock_by_pid = { _i(r["product_id"]): r for r in _product_stock_rows(db, 500) }
        recent_units = _product_units_in_range(db, rs, re, None, None)
        recs_list = []

        for row in recent_units:
            pid = _i(row.get("product_id"))
            name = str(row.get("product_name") or "N/A")
            ru = _i(row.get("units"))
            daily = ru / days
            predicted = daily * days
            stock = _i(stock_by_pid.get(pid, {}).get("stock_total")) if pid in stock_by_pid else 0
            target = predicted * sf
            gap = max(0, int(round(target - stock)))
            if gap <= 0:
                continue
            priority = "high" if gap > stock and stock < 10 else "medium" if gap > 5 else "low"
            recs_list.append(
                {
                    "product_id": pid,
                    "product_name": name,
                    "current_stock": stock,
                    "units_sold_recent_window": ru,
                    "predicted_demand_units": round(predicted, 1),
                    "suggested_production_or_restock_qty": gap,
                    "priority": priority,
                    "reason": f"Demanda reciente ~{ru} uds/{days}d; stock {stock}; objetivo con factor {sf}.",
                }
            )

        recs_list.sort(
            key=lambda x: (
                {"high": 0, "medium": 1, "low": 2}.get(x["priority"], 3),
                -x["suggested_production_or_restock_qty"],
            ),
        )
        top = recs_list[:15]
        summary = (
            f"{len(top)} productos sugieren reposición/producción en base a demanda de {days} días."
            if top
            else "No hay brechas claras entre stock y demanda reciente."
        )
        recommendations = [
            f"Prioriza {x['product_name']} (ID {x['product_id']}): producir/comprar ~{x['suggested_production_or_restock_qty']} uds ({x['priority']})."
            for x in top[:5]
        ]
        if not recommendations:
            recommendations = [
                "Mantén revisión semanal: si aparecen quiebres de stock, reduce el umbral de días o sube el factor de seguridad.",
            ]
        return {
            "summary": summary,
            "data": {"window_days": days, "safety_factor": sf, "items": top},
            "recommendations": recommendations,
            "generated_at": _iso_now(),
        }
    except Exception as exc:
        return {
            "summary": "No se pudieron calcular recomendaciones de producción.",
            "data": {"error": str(exc)},
            "recommendations": ["Revisa inventario y ventas completadas."],
            "generated_at": _iso_now(),
        }


def build_anomaly_detection(
    db: Session,
    days_recent: int = 14,
    days_baseline: int = 28,
) -> dict[str, Any]:
    """Caídas/picos de ingresos tienda + productos con baja rotación y stock alto."""
    dr = max(7, min(int(days_recent), 90))
    db_ = max(14, min(int(days_baseline), 120))
    end = datetime.now()
    recent_start = end - timedelta(days=dr)
    base_end = recent_start
    base_start = base_end - timedelta(days=db_)

    anomalies: list[dict[str, Any]] = []

    try:
        rev_r = _store_revenue_completed(db, recent_start, end)
        rev_b = _store_revenue_completed(db, base_start, base_end)
        daily_r = rev_r / dr if dr else 0
        daily_b = rev_b / db_ if db_ else 0

        if daily_b > 0 and daily_r < daily_b * 0.7:
            anomalies.append(
                {
                    "anomaly_type": "revenue_drop",
                    "severity": "high",
                    "description": f"Ingresos recientes ({dr}d) ~{daily_r:.0f}/día vs línea base ~{daily_b:.0f}/día.",
                    "affected_products": [],
                    "recommended_action": "Revisar conversión, precios, stock roto y campañas; comparar con mismo periodo anterior.",
                }
            )
        elif daily_b > 0 and daily_r > daily_b * 1.5:
            anomalies.append(
                {
                    "anomaly_type": "revenue_spike",
                    "severity": "medium",
                    "description": f"Pico de ingresos recientes ({dr}d) frente a línea base.",
                    "affected_products": [],
                    "recommended_action": "Asegura inventario y tiempos de envío; identifica SKUs impulsores.",
                }
            )

        # Baja rotación: pocas ventas en 60d pero stock alto
        rs60 = end - timedelta(days=60)
        slow_q = text("""
            WITH product_stock AS (
                SELECT p.id, p.name,
                    COALESCE(SUM(c.stock), 0)::BIGINT AS stock_total
                FROM tab_products p
                LEFT JOIN tab_product_variant_groups g ON g.product_id = p.id
                LEFT JOIN tab_product_variant_combinations c ON c.group_id = g.id AND c.is_active = TRUE
                WHERE p.is_active = TRUE
                GROUP BY p.id, p.name
            ),
            sales60 AS (
                SELECT p.id AS product_id,
                    COALESCE(SUM(op.cant_producto), 0)::BIGINT AS u
                FROM tab_products p
                LEFT JOIN tab_product_variant_groups g ON g.product_id = p.id
                LEFT JOIN tab_product_variant_combinations pv ON pv.group_id = g.id AND pv.is_active = TRUE
                LEFT JOIN tab_orden_productos op ON op.variant_id = pv.id
                LEFT JOIN tab_ordenes o ON op.id_orden = o.id_orden
                    AND o.ind_estado = :completed
                    AND o.fec_pedido >= :rs60
                    AND o.fec_pedido <= :end_ts
                WHERE p.is_active = TRUE
                GROUP BY p.id
            )
            SELECT ps.id AS product_id, ps.name AS product_name, ps.stock_total, COALESCE(s.u, 0) AS units_60d
            FROM product_stock ps
            LEFT JOIN sales60 s ON s.product_id = ps.id
            WHERE ps.stock_total >= 15 AND COALESCE(s.u, 0) <= 2
            ORDER BY ps.stock_total DESC
            LIMIT 12
        """)
        slow_rows = db.execute(
            slow_q,
            {
                "completed": ORDER_COMPLETED_STATUS,
                "rs60": rs60,
                "end_ts": end,
            },
        ).mappings().all()
        if slow_rows:
            affected = [
                {"product_id": _i(r["product_id"]), "name": r["product_name"], "stock": _i(r["stock_total"])}
                for r in slow_rows
            ]
            anomalies.append(
                {
                    "anomaly_type": "low_rotation_high_stock",
                    "severity": "medium",
                    "description": "Productos con stock alto y casi sin ventas en 60 días.",
                    "affected_products": affected,
                    "recommended_action": "Promociones, bundles, o reducir compras; evaluar descontinuar variantes.",
                }
            )

        summary = (
            f"Se detectaron {len(anomalies)} alertas de negocio."
            if anomalies
            else "No se detectaron anomalías fuertes con las reglas actuales."
        )
        recommendations = [a["recommended_action"] for a in anomalies][:5]
        if not recommendations:
            recommendations = ["Mantén monitoreo semanal de ingresos y stock lento."]
        return {
            "summary": summary,
            "data": {
                "windows": {"recent_days": dr, "baseline_days": db_},
                "store_revenue_recent": round(rev_r, 2),
                "store_revenue_baseline": round(rev_b, 2),
                "anomalies": anomalies,
            },
            "recommendations": recommendations,
            "generated_at": _iso_now(),
        }
    except Exception as exc:
        return {
            "summary": "Error al detectar anomalías.",
            "data": {"error": str(exc)},
            "recommendations": ["Intenta de nuevo o revisa conectividad a la base de datos."],
            "generated_at": _iso_now(),
        }


# Categorías con mayor afinidad export (heurística simple por palabras clave en nombre)
_EXPORT_KEYWORDS = (
    "cosmetic", "cosmétic", "skin", "belleza", "beauty", "organic", "organico",
    "food", "snack", "coffee", "café", "tea", "tech", "electronic",
)


def build_export_readiness(db: Session, limit: int = 10) -> dict[str, Any]:
    """
    Productos con buen desempeño reciente + consistencia (ventas período anterior > 0).
    Mercados sugeridos sin APIs externas.
    """
    days = 30
    rs, re, ps, pe = _window_bounds(days)
    lim = max(1, min(int(limit), 25))

    try:
        recent = _product_units_in_range(db, rs, re, None, None)
        prev = _product_units_in_range(db, ps, pe, None, None)
        prev_map = {_i(r["product_id"]): _i(r["units"]) for r in prev}

        candidates = []
        for r in recent:
            pid = _i(r["product_id"])
            name = str(r.get("product_name") or "")
            ur = _i(r.get("units"))
            up = prev_map.get(pid, 0)
            if ur < 5:
                continue
            consistency = min(1.0, up / max(ur, 1)) if ur else 0.0
            score = min(100, ur * 2 + up + (10 if consistency > 0.5 else 0))
            cat_hint = "general"
            low = name.lower()
            for kw in _EXPORT_KEYWORDS:
                if kw in low:
                    cat_hint = "differentiated_product"
                    break
            candidates.append(
                {
                    "product_id": pid,
                    "product_name": name,
                    "units_recent": ur,
                    "units_previous": up,
                    "readiness_score": int(score),
                    "category_heuristic": cat_hint,
                }
            )
        candidates.sort(key=lambda x: x["readiness_score"], reverse=True)
        top = candidates[:lim]

        markets = [
            {"region": "México", "note": "TMEC y proximidad cultural; validar etiquetado."},
            {"region": "Chile", "note": "Mercado retail estable; revisar aranceles sectoriales."},
            {"region": "Unión Europea", "note": "Exige cumplimiento regulatorio (ej. cosmética, alimentos)."},
        ]

        summary = (
            f"{len(top)} productos muestran potencial export inicial por volumen y consistencia."
            if top
            else "Datos insuficientes para candidatos export (necesitas más ventas recientes)."
        )
        recommendations = [
            "Prioriza 1–2 SKU piloto con demanda estable y margen saludable.",
            "Documenta ficha técnica, origen y cumplimiento para el mercado destino.",
            "Valida logística internacional (INCOTERMS) antes de escalar.",
        ]
        return {
            "summary": summary,
            "data": {"candidates": top, "suggested_markets": markets},
            "recommendations": recommendations,
            "generated_at": _iso_now(),
        }
    except Exception as exc:
        return {
            "summary": "No se pudo evaluar preparación para exportación.",
            "data": {"error": str(exc)},
            "recommendations": [],
            "generated_at": _iso_now(),
        }


def build_business_insights(db: Session) -> dict[str, Any]:
    """Agrega predicción, producción, anomalías y export con degradación parcial."""
    parts: dict[str, Any] = {}
    errors: list[str] = []

    for key, fn in (
        ("demand", lambda: build_demand_prediction(db, None, None, 30)),
        ("production", lambda: build_production_recommendations(db, 30, 1.15)),
        ("anomalies", lambda: build_anomaly_detection(db, 14, 28)),
        ("export", lambda: build_export_readiness(db, 8)),
    ):
        try:
            parts[key] = fn()
        except Exception as e:
            errors.append(f"{key}: {e}")
            parts[key] = {
                "summary": f"No disponible ({key}).",
                "data": {},
                "recommendations": [],
                "generated_at": _iso_now(),
            }

    summary_lines = []
    for k, v in parts.items():
        s = v.get("summary") if isinstance(v, dict) else ""
        if s:
            summary_lines.append(f"- **{k}**: {s}")

    all_recs: list[str] = []
    for v in parts.values():
        if isinstance(v, dict):
            for r in v.get("recommendations") or []:
                if r and r not in all_recs:
                    all_recs.append(r)
    all_recs = all_recs[:12]

    if errors:
        all_recs.append("Algunos módulos fallaron: " + "; ".join(errors[:3]))

    return {
        "summary": "Panorama inteligencia de negocio:\n" + "\n".join(summary_lines)
        if summary_lines
        else "Insights agregados.",
        "data": parts,
        "recommendations": all_recs
        or ["Abre cada sección en el Centro de Decisiones para más detalle."],
        "generated_at": _iso_now(),
    }
