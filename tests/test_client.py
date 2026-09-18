"""Pruebas unitarias para BanxicoClient."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from mcp_banxico.client import BanxicoAPIError, BanxicoClient


@pytest.mark.asyncio
async def test_client_missing_token_raises_helpful_error():
    client = BanxicoClient(token="")
    with pytest.raises(BanxicoAPIError, match="No se encontró el token de Banxico"):
        await client.get_series_data("SF43718")


@pytest.mark.asyncio
async def test_client_get_series_data_success():
    client = BanxicoClient(token="mock_token_123")

    mock_response_data = {
        "bmx": {
            "series": [
                {
                    "idSerie": "SF43718",
                    "titulo": "Tipo de cambio pesos por dólar E.U.A. FIX",
                    "datos": [{"fecha": "18/09/2026", "dato": "19.85"}],
                }
            ]
        }
    }

    mock_response = httpx.Response(200, json=mock_response_data)
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_series_data("SF43718")

        assert result["id_serie"] == "SF43718"
        assert result["titulo"] == "Tipo de cambio pesos por dólar E.U.A. FIX"
        assert len(result["datos"]) == 1
        assert result["datos"][0]["dato"] == "19.85"


@pytest.mark.asyncio
async def test_client_get_series_data_unauthorized():
    client = BanxicoClient(token="invalid_token")

    mock_response = httpx.Response(401, json={"error": "Unauthorized"})
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        with pytest.raises(BanxicoAPIError, match="Token de Banxico inválido o no autorizado"):
            await client.get_series_data("SF43718")


@pytest.mark.asyncio
async def test_client_get_series_data_server_error():
    client = BanxicoClient(token="mock_token")

    mock_response = httpx.Response(500, text="Internal Server Error")
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        with pytest.raises(BanxicoAPIError, match="Banxico respondió con código HTTP 500"):
            await client.get_series_data("SF43718")


@pytest.mark.asyncio
async def test_client_get_latest_value():
    client = BanxicoClient(token="mock_token")

    mock_response_data = {
        "bmx": {
            "series": [
                {
                    "idSerie": "SP68254",
                    "titulo": "Valor de la UDI",
                    "datos": [{"fecha": "18/09/2026", "dato": "8.145023"}],
                }
            ]
        }
    }

    mock_response = httpx.Response(200, json=mock_response_data)
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await client.get_latest_value("UDIS")

        assert result["serie"] == "UDIS"
        assert result["id_serie"] == "SP68254"
        assert result["valor"] == "8.145023"
        assert result["fecha"] == "18/09/2026"


@pytest.mark.asyncio
async def test_client_unknown_series_key_raises_error():
    client = BanxicoClient(token="mock_token")
    with pytest.raises(BanxicoAPIError, match="no reconocida en el catálogo"):
        await client.get_latest_value("SERIE_INEXISTENTE")
