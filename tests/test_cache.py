"""Pruebas de la caché en memoria del BanxicoClient.

La caché existe para que el endpoint hospedado no queme el límite de
consultas del token compartido: los datos del SIE cambian una vez al día
como mucho, así que repetir la llamada HTTP por cada petición es desperdicio.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from mcp_banxico.client import BanxicoAPIError, BanxicoClient


def _respuesta(valor: str = "19.85") -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "bmx": {
                "series": [
                    {
                        "idSerie": "SF43718",
                        "titulo": "Tipo de cambio FIX",
                        "datos": [{"fecha": "25/09/2026", "dato": valor}],
                    }
                ]
            }
        },
    )


@pytest.mark.asyncio
async def test_segunda_llamada_identica_no_vuelve_a_pegarle_a_banxico():
    client = BanxicoClient(token="tok", cache_ttl=3600)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = _respuesta()

        primero = await client.get_series_data("SF43718")
        segundo = await client.get_series_data("SF43718")

        assert mock_get.call_count == 1
        assert primero == segundo


@pytest.mark.asyncio
async def test_parametros_distintos_no_comparten_entrada():
    client = BanxicoClient(token="tok", cache_ttl=3600)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = _respuesta()

        await client.get_series_data("SF43718")
        await client.get_series_data("SF43718", fecha_inicio="2026-01-01")
        await client.get_series_data("SF60653")

        assert mock_get.call_count == 3


@pytest.mark.asyncio
async def test_entrada_expirada_se_vuelve_a_consultar(monkeypatch):
    client = BanxicoClient(token="tok", cache_ttl=60)
    reloj = {"t": 1000.0}
    monkeypatch.setattr("mcp_banxico.client.monotonic", lambda: reloj["t"])

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = _respuesta()

        await client.get_series_data("SF43718")
        reloj["t"] += 59
        await client.get_series_data("SF43718")
        assert mock_get.call_count == 1, "dentro del TTL debe servirse de caché"

        reloj["t"] += 2
        await client.get_series_data("SF43718")
        assert mock_get.call_count == 2, "pasado el TTL debe reconsultar"


@pytest.mark.asyncio
async def test_los_errores_no_se_cachean():
    client = BanxicoClient(token="tok", cache_ttl=3600)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = httpx.Response(500, text="boom")
        with pytest.raises(BanxicoAPIError):
            await client.get_series_data("SF43718")

        mock_get.return_value = _respuesta()
        resultado = await client.get_series_data("SF43718")

        assert mock_get.call_count == 2
        assert resultado["id_serie"] == "SF43718"


@pytest.mark.asyncio
async def test_ttl_cero_desactiva_la_cache():
    client = BanxicoClient(token="tok", cache_ttl=0)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = _respuesta()

        await client.get_series_data("SF43718")
        await client.get_series_data("SF43718")

        assert mock_get.call_count == 2


@pytest.mark.asyncio
async def test_llamadas_concurrentes_iguales_disparan_una_sola_consulta():
    """Sin esto, N peticiones simultáneas al arrancar en frío son N golpes al SIE."""
    import asyncio

    client = BanxicoClient(token="tok", cache_ttl=3600)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = _respuesta()

        await asyncio.gather(*(client.get_series_data("SF43718") for _ in range(8)))

        assert mock_get.call_count == 1


@pytest.mark.asyncio
async def test_la_cache_no_crece_sin_limite():
    """`consultar_serie_sie` acepta IDs arbitrarios: sin cota, un endpoint
    público se puede llenar de memoria con claves basura."""
    client = BanxicoClient(token="tok", cache_ttl=3600, cache_max_entries=50)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = _respuesta()

        for i in range(200):
            await client.get_series_data(f"SERIE{i}")

        assert len(client._cache) <= 50
        assert len(client._locks) <= 50
