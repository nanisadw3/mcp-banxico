"""Pruebas unitarias para el servidor MCPServer de Banxico."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest

from mcp_banxico.server import create_server


def _extract_text(raw_result) -> str:
    """Extrae el contenido de texto del resultado de una llamada a herramienta MCP."""
    if hasattr(raw_result, "content") and raw_result.content:
        return raw_result.content[0].text
    if isinstance(raw_result, list) and raw_result:
        return getattr(raw_result[0], "text", str(raw_result[0]))
    return str(raw_result)


@pytest.fixture
def server():
    return create_server(token="test_token")


@pytest.mark.asyncio
async def test_server_tools_registered(server):
    tools = await server.list_tools()
    tool_names = [t.name for t in tools]

    assert "tipo_cambio_usd" in tool_names
    assert "inflacion_mexico" in tool_names
    assert "valor_udis" in tool_names
    assert "tasa_interes_banxico" in tool_names
    assert "reservas_internacionales" in tool_names
    assert "consultar_serie_sie" in tool_names


@pytest.mark.asyncio
async def test_tool_tipo_cambio_usd_success(server):
    mock_data = {
        "serie": "TIPO_CAMBIO_FIX",
        "id_serie": "SF43718",
        "nombre": "Tipo de cambio FIX",
        "descripcion": "FIX",
        "fecha": "18/09/2026",
        "valor": "19.92",
    }

    with patch(
        "mcp_banxico.client.BanxicoClient.get_latest_value", new_callable=AsyncMock
    ) as mock_val:
        mock_val.return_value = mock_data

        raw = await server.call_tool("tipo_cambio_usd", {"tipo": "FIX"})
        text_content = _extract_text(raw)
        data = json.loads(text_content)

        assert data["valor"] == "19.92"
        assert data["fecha"] == "18/09/2026"


@pytest.mark.asyncio
async def test_tool_tipo_cambio_usd_date_range(server):
    mock_series_data = {
        "id_serie": "SF43718",
        "titulo": "Tipo de cambio FIX",
        "datos": [
            {"fecha": "17/09/2026", "dato": "19.80"},
            {"fecha": "18/09/2026", "dato": "19.92"},
        ],
    }

    with patch(
        "mcp_banxico.client.BanxicoClient.get_series_data", new_callable=AsyncMock
    ) as mock_data:
        mock_data.return_value = mock_series_data

        raw = await server.call_tool(
            "tipo_cambio_usd",
            {"tipo": "FIX", "fecha_inicio": "2026-09-17", "fecha_fin": "2026-09-18"},
        )
        text_content = _extract_text(raw)
        data = json.loads(text_content)

        assert data["serie_id"] == "SF43718"
        assert len(data["observaciones"]) == 2


@pytest.mark.asyncio
async def test_tool_inflacion_mexico_success(server):
    mock_data = {
        "serie": "INFLACION_ANUAL",
        "id_serie": "SP74625",
        "nombre": "Inflación Anual (INPC)",
        "descripcion": "Variación porcentual anual",
        "fecha": "08/2026",
        "valor": "4.99",
    }

    with patch(
        "mcp_banxico.client.BanxicoClient.get_latest_value", new_callable=AsyncMock
    ) as mock_val:
        mock_val.return_value = mock_data

        raw = await server.call_tool("inflacion_mexico", {"tipo": "anual"})
        text_content = _extract_text(raw)
        data = json.loads(text_content)

        assert data["valor"] == "4.99"


@pytest.mark.asyncio
async def test_tool_valor_udis_success(server):
    mock_data = {
        "serie": "UDIS",
        "id_serie": "SP68254",
        "nombre": "Valor de la UDI",
        "descripcion": "UDI",
        "fecha": "18/09/2026",
        "valor": "8.14",
    }

    with patch(
        "mcp_banxico.client.BanxicoClient.get_latest_value", new_callable=AsyncMock
    ) as mock_val:
        mock_val.return_value = mock_data

        raw = await server.call_tool("valor_udis", {})
        text_content = _extract_text(raw)
        data = json.loads(text_content)

        assert data["valor"] == "8.14"


@pytest.mark.asyncio
async def test_tool_tasa_interes_banxico_success(server):
    mock_data = {
        "serie": "TIIE_28",
        "id_serie": "SF61745",
        "nombre": "TIIE 28 días",
        "descripcion": "TIIE",
        "fecha": "18/09/2026",
        "valor": "10.75",
    }

    with patch(
        "mcp_banxico.client.BanxicoClient.get_latest_value", new_callable=AsyncMock
    ) as mock_val:
        mock_val.return_value = mock_data

        raw = await server.call_tool("tasa_interes_banxico", {"tipo": "tiie_28"})
        text_content = _extract_text(raw)
        data = json.loads(text_content)

        assert data["valor"] == "10.75"


@pytest.mark.asyncio
async def test_tool_reservas_internacionales_success(server):
    mock_data = {
        "serie": "RESERVAS_INTERNACIONALES",
        "id_serie": "SF46410",
        "nombre": "Reservas Internacionales",
        "descripcion": "Reservas",
        "fecha": "12/09/2026",
        "valor": "225000",
    }

    with patch(
        "mcp_banxico.client.BanxicoClient.get_latest_value", new_callable=AsyncMock
    ) as mock_val:
        mock_val.return_value = mock_data

        raw = await server.call_tool("reservas_internacionales", {})
        text_content = _extract_text(raw)
        data = json.loads(text_content)

        assert data["valor"] == "225000"


@pytest.mark.asyncio
async def test_tool_consultar_serie_sie_success(server):
    mock_series_data = {
        "id_serie": "SF43718",
        "titulo": "Tipo de cambio",
        "datos": [{"fecha": "18/09/2026", "dato": "19.85"}],
    }

    with patch(
        "mcp_banxico.client.BanxicoClient.get_series_data", new_callable=AsyncMock
    ) as mock_series:
        mock_series.return_value = mock_series_data

        raw = await server.call_tool("consultar_serie_sie", {"id_serie": "SF43718"})
        text_content = _extract_text(raw)
        data = json.loads(text_content)

        assert data["id_serie"] == "SF43718"
        assert len(data["datos"]) == 1
