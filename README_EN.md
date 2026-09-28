# 🇲🇽 mcp-banxico

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Protocol_2.0-purple.svg)](https://modelcontextprotocol.io/)

Community Model Context Protocol (MCP) server for querying official economic indicators and exchange rates from the **Central Bank of Mexico (Banco de México - Banxico SIE)**.

Enables AI agents and assistants (**Claude Desktop**, **Cursor**, **Cline**, **Gemini CLI**) to retrieve real-time USD/MXN exchange rates (FIX & liquidation), inflation (CPI / INPC), UDIS investment units, interbank interest rates (TIIE), and international reserves.

> **Independent project.** Not affiliated with or endorsed by Banco de México.
> It reads the public SIE API.

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
