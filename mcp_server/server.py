# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp"]
# ///
"""MCP de reporteria Odoo — stadistic_ia.

3 tools genericas sobre XML-RPC: consultar, agrupar, listar_campos.
Config via env: ODOO_URL, ODOO_DB, ODOO_USER, ODOO_API_KEY.
"""
import json
import os
import xmlrpc.client

from mcp.server.fastmcp import FastMCP

URL = os.environ.get("ODOO_URL", "http://localhost:8069")
DB = os.environ.get("ODOO_DB", "")
USER = os.environ.get("ODOO_USER", "")
KEY = os.environ.get("ODOO_API_KEY", "")

mcp = FastMCP("stadistic-ia")
_uid = None


def _execute(model: str, method: str, args: list, kwargs: dict | None = None):
    global _uid
    if _uid is None:
        _uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USER, KEY, {})
        if not _uid:
            raise RuntimeError(f"Autenticacion fallida: db={DB} user={USER}")
    proxy = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    return proxy.execute_kw(DB, _uid, KEY, model, method, args, kwargs or {})


def _json(data) -> str:
    return json.dumps(data, ensure_ascii=False, default=str)


@mcp.tool()
def consultar(model: str, domain: list = [], fields: list = [], limit: int = 50, order: str = "") -> str:
    """Lee registros de un modelo Odoo (search_read).

    Args:
        model: modelo Odoo, ej. 'sale.order', 'product.product', 'stock.quant'.
        domain: filtro Odoo, ej. [["date_order", ">=", "2026-01-01"]].
        fields: campos a devolver, ej. ["name", "amount_total"]. SIEMPRE pasar
            fields — sin ellos devuelve todos los campos y la respuesta es enorme.
        limit: maximo de registros (default 50).
        order: orden, ej. "amount_total desc".
    """
    kw = {"fields": fields, "limit": limit}
    if order:
        kw["order"] = order
    return _json(_execute(model, "search_read", [domain], kw))


@mcp.tool()
def agrupar(model: str, domain: list = [], groupby: list = [], aggregates: list = [], limit: int = 100) -> str:
    """Agrega datos de un modelo Odoo (read_group). Ideal para reporteria.

    Modelos utiles: 'sale.report' (ventas), 'purchase.report' (compras),
    'stock.quant' (inventario), 'account.invoice.report' (facturacion).

    Args:
        model: modelo Odoo.
        domain: filtro Odoo, ej. [["date", ">=", "2026-06-01"]].
        groupby: campos de agrupacion, ej. ["partner_id"], ["date:month"],
            ["product_id", "date:month"].
        aggregates: campos con agregado, ej. ["price_total:sum",
            "product_uom_qty:sum", "quantity:sum"].
        limit: maximo de grupos (default 100).

    Devuelve grupos con '__count' (num registros) y los agregados pedidos.
    """
    return _json(_execute(
        model, "read_group",
        [domain, aggregates, groupby],
        {"lazy": False, "limit": limit},
    ))


@mcp.tool()
def listar_campos(model: str, buscar: str = "") -> str:
    """Lista campos de un modelo Odoo (nombre, etiqueta, tipo, relacion).

    Usar antes de consultar/agrupar si no se conocen los campos exactos.

    Args:
        model: modelo Odoo, ej. 'sale.report'.
        buscar: filtro opcional por texto en nombre o etiqueta, ej. 'fecha'.
    """
    fields = _execute(model, "fields_get", [], {"attributes": ["string", "type", "relation"]})
    if buscar:
        b = buscar.lower()
        fields = {k: v for k, v in fields.items()
                  if b in k.lower() or b in (v.get("string") or "").lower()}
    return _json(fields)


if __name__ == "__main__":
    mcp.run()
