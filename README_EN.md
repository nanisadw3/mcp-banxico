# 🇲🇽 mcp-banxico

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Protocol_2.0-purple.svg)](https://modelcontextprotocol.io/)

Community Model Context Protocol (MCP) server for querying official economic indicators and exchange rates from the **Central Bank of Mexico (Banco de México - Banxico SIE)**.

Enables AI agents and assistants (**Claude Desktop**, **Cursor**, **Cline**, **Gemini CLI**) to retrieve real-time USD/MXN exchange rates (FIX & liquidation), inflation (CPI / INPC), UDIS investment units, interbank interest rates (TIIE), and international reserves.

> **Independent project.** Not affiliated with or endorsed by Banco de México.
> It reads the public SIE API.

## ▶️ Video demo

[![Así conecté Claude al Banco de México (video demo, in Spanish)](https://img.youtube.com/vi/saaD665cn9g/maxresdefault.jpg)](https://www.youtube.com/watch?v=saaD665cn9g)

Ten-minute uncut demo (in Spanish): a local model (Qwen 2.5 on Ollama) and Claude Desktop go from *"I don't have real-time access"* to answering with the official exchange rate. The key moment is at [2:52](https://www.youtube.com/watch?v=saaD665cn9g&t=172s).

---

## ⚡ Quick Start

### Option 0 — Hosted endpoint (no install, no token)

A public instance is available. Nothing to install and no Banxico token to
request — the hosted instance carries its own:

```
https://banxico-mcp.duckdns.org/mcp
```

Streamable HTTP. In `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "banxico": {
      "type": "streamable-http",
      "url": "https://banxico-mcp.duckdns.org/mcp"
    }
  }
}
```

> Community service on self-hosted infrastructure, rate limited per IP. For
> heavy or production use, install it locally with your own token so you don't
> depend on this instance staying up.

#### Trying it by hand (curl or Postman)

The endpoint speaks JSON-RPC 2.0 over HTTP POST. Two requests: one to open a
session, one to call the tool.

**1. Open a session.** The response carries an `mcp-session-id` header:

```bash
curl -i -X POST https://banxico-mcp.duckdns.org/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-06-18",
      "capabilities": {},
      "clientInfo": { "name": "curl", "version": "1" }
    }
  }'
```

**2. Call a tool**, passing that id as a header:

```bash
curl -X POST https://banxico-mcp.duckdns.org/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'mcp-session-id: ID_FROM_STEP_1' \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": { "name": "tipo_cambio_usd", "arguments": {} }
  }'
```

Response (the payload arrives as an SSE event, on the `data:` line):

```json
{
  "serie": "TIPO_CAMBIO_FIX",
  "id_serie": "SF43718",
  "nombre": "Tipo de cambio FIX (Pesos por Dólar)",
  "unidad": "Pesos por dólar",
  "fecha": "28/09/2026",
  "valor": "17.8413"
}
```

Other `params` examples:

```json
{ "name": "inflacion_mexico",         "arguments": { "tipo": "anual" } }
{ "name": "valor_udis",               "arguments": {} }
{ "name": "tasa_interes_banxico",     "arguments": { "tipo": "objetivo" } }
{ "name": "reservas_internacionales", "arguments": {} }
{ "name": "consultar_serie_sie",      "arguments": { "id_serie": "SF43718",
                                                     "fecha_inicio": "2026-09-01",
                                                     "fecha_fin": "2026-09-28" } }
```

> **Two things that trip people up in Postman.**
> `mcp-session-id` is required from the second request onward — without it you
> get `400`. And sending `Accept: application/json` alone returns `406`: the
> server requires **both** media types, or you can omit the header entirely.

### Option 1 — Local install

```bash
uvx mcp-banxico
```

### Claude Desktop Configuration (local install)

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "banxico": {
      "command": "uvx",
      "args": ["mcp-banxico"],
      "env": {
        "BANXICO_TOKEN": "YOUR_BANXICO_TOKEN"
      }
    }
  }
}
```

Free tokens can be requested at: [Banxico SIE API Token Portal](https://www.banxico.org.mx/SieAPIRest/service/v1/token).

## 🌐 Self-hosting a remote instance

```bash
mcp-banxico --transport streamable-http \
            --host 127.0.0.1 --port 8005 \
            --allowed-host your-domain.example
```

`--allowed-host` is required behind a reverse proxy: the HTTP transport
validates the `Host` header against DNS rebinding attacks and answers `421` to
every request unless the public name is declared.

The in-memory cache (1 h by default, tune with `BANXICO_CACHE_TTL`) keeps a
shared token from exhausting its SIE quota.

## Available Tools

* `tipo_cambio_usd`: Official USD/MXN exchange rate (FIX and settlement rate).
* `inflacion_mexico`: Annual or monthly inflation rate based on the National Consumer Price Index (INPC).
* `valor_udis`: Official value of Mexico's Investment Units (UDIS).
* `tasa_interes_banxico`: Interbank Equilibrium Interest Rate (TIIE 28 days) or Target Monetary Policy Rate.
* `reservas_internacionales`: Net international reserves balance in million USD.
* `consultar_serie_sie`: Free query for any economic series identifier in Banxico's SIE catalog.

## License

MIT License. Developed by **[Inaki Sobera (nanisadw3)](https://github.com/nanisadw3)**.
