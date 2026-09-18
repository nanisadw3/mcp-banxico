"""Cliente HTTP asíncrono para consumir la API oficial del Banco de México (SIE)."""

from __future__ import annotations

import os
from typing import Any

import httpx

from .constants import BANXICO_API_BASE_URL, BANXICO_TOKEN_HELP_URL, SERIES


class BanxicoAPIError(Exception):
    """Excepción para errores al consultar la API de Banxico."""



class BanxicoClient:
    """Cliente para interactuar con la API SIE de Banxico."""

    def __init__(self, token: str | None = None, timeout: float = 10.0):
        self.token = token or os.environ.get("BANXICO_TOKEN", "")
        self.timeout = timeout

    def _get_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "mcp-banxico/0.1.0 (https://github.com/nanisadw3/mcp-banxico)",
        }
        if self.token:
            headers["Bmx-Token"] = self.token
        return headers

    async def get_series_data(
        self,
        series_id: str,
        fecha_inicio: str | None = None,
        fecha_fin: str | None = None,
    ) -> dict[str, Any]:
        """Consulta observaciones para una serie de Banxico.

        Si no se especifican fechas, consulta el dato oportuno (más reciente).
        """
        if not self.token:
            raise BanxicoAPIError(
                "No se encontró el token de Banxico. "
                f"Obtén tu token gratuito en {BANXICO_TOKEN_HELP_URL} "
                "y configúralo en la variable de entorno BANXICO_TOKEN."
            )

        if fecha_inicio and fecha_fin:
            url = f"{BANXICO_API_BASE_URL}/{series_id}/datos/{fecha_inicio}/{fecha_fin}"
        elif fecha_inicio:
            url = f"{BANXICO_API_BASE_URL}/{series_id}/datos/{fecha_inicio}/{fecha_inicio}"
        else:
            url = f"{BANXICO_API_BASE_URL}/{series_id}/datos/oportuno"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=self._get_headers())
            except httpx.RequestError as e:
                raise BanxicoAPIError(f"Error de red al conectar con Banxico: {e}") from e

            if response.status_code == 401 or response.status_code == 403:
                raise BanxicoAPIError(
                    "Token de Banxico inválido o no autorizado. "
                    f"Verifica tu clave en {BANXICO_TOKEN_HELP_URL}."
                )
            if response.status_code != 200:
                raise BanxicoAPIError(
                    f"Banxico respondió con código HTTP {response.status_code}: {response.text}"
                )

            try:
                data = response.json()
            except Exception as e:
                raise BanxicoAPIError(f"Error al decodificar respuesta JSON de Banxico: {e}") from e

        series_list = data.get("bmx", {}).get("series", [])
        if not series_list:
            raise BanxicoAPIError(f"No se encontraron datos para la serie '{series_id}'.")

        serie = series_list[0]
        return {
            "id_serie": serie.get("idSerie"),
            "titulo": serie.get("titulo"),
            "datos": serie.get("datos", []),
        }

    async def get_latest_value(self, series_key: str) -> dict[str, Any]:
        """Obtiene el último valor registrado de una serie del catálogo."""
        if series_key not in SERIES:
            raise BanxicoAPIError(f"Serie '{series_key}' no reconocida en el catálogo.")

        info = SERIES[series_key]
        raw = await self.get_series_data(info["id"])
        datos = raw.get("datos", [])
        ultimo = datos[-1] if datos else {}

        return {
            "serie": series_key,
            "id_serie": info["id"],
            "nombre": info["nombre"],
            "descripcion": info["descripcion"],
            "fecha": ultimo.get("fecha", "N/D"),
            "valor": ultimo.get("dato", "N/D"),
        }
