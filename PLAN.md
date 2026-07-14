# Plan: MCP reportería Odoo — stadistic_ia

Servidor MCP en Python conectado a Odoo 19 local (Docker, puerto 8069) vía XML-RPC.
Claude consulta ventas / compras / productos / inventario con tools genéricas.

## Fase 0 — Preparar Odoo (manual, navegador)
- [x] BD `pruebas2` con datos demo
- [x] Apps: Ventas, Compras, Inventario
- [x] Usuario `iacmp@gmail.com` + API key


## Fase 1 — Servidor MCP
Estructura mínima:
```
mcp_server/
└── server.py     # FastMCP + xmlrpc.client (stdlib). Única dep: mcp
```
3 tools genéricas (cubren cualquier reporte):
- `consultar(model, domain, fields, limit)` → `search_read`
- `agrupar(model, domain, groupby, aggregates)` → `read_group`
- `listar_campos(model)` → `fields_get`

Modelos clave: `sale.report`, `purchase.report`, `stock.quant`, `product.product`.

Reglas:
- Respuestas JSON compactas, `limit` default (contexto de Claude no aguanta dumps).
- Docstrings en español — Claude los lee para elegir tool.

## Fase 1 — HECHO
- [x] `mcp_server/server.py` — FastMCP + xmlrpc, 3 tools, deps inline (uv)
- [x] Smoke test tools OK contra pruebas2

## Fase 2 — Conectar Claude
- [x] `.mcp.json` creado (comando: `uv run mcp_server/server.py`)
- [ ] Reiniciar sesion Claude Code y aprobar server
- [ ] `.mcp.json` en raíz del proyecto:
```json
{ "mcpServers": { "stadistic-ia": {
    "command": "python",
    "args": ["mcp_server/server.py"],
    "env": {
      "ODOO_URL": "http://localhost:8069",
      "ODOO_DB": "<nombre-bd>",
      "ODOO_USER": "mcp_bot",
      "ODOO_API_KEY": "<api-key>"
    }
}}}
```
- [ ] Smoke test: "¿cuánto vendimos este mes por vendedor?"

## Fase 3 — Después del MVP (solo si hace falta)
- Tools especializadas si Claude falla armando domains solo
- Comparativas de períodos, márgenes
- SQL directo a Postgres si RPC queda corto (exponer 5432; salta seguridad Odoo — último recurso)
